"""esco_linker.py: link a text to the ESCO skills-pillar concept of its most similar label (addendum 1, 3.2).

Every concept is represented by its preferred label and its alternative labels (ESCO v1.2.1, English,
`esco_skills_v1.2.1_en.csv.gz`). Labels and texts are embedded with sentence-transformers/all-mpnet-base-v2
at a pinned revision (normalised embeddings, so the dot product is the cosine similarity). A text links to
the concept that owns its most similar label; it is linked only if that cosine is at least the cutoff
(registered 0.5; sensitivity: no cutoff, and 0.7). If the most similar label text is shared by several
concepts, the first concept in URI order wins (the label table is built in that order and argmax returns
the first maximum).

Texts are embedded exactly as written (outer whitespace stripped, nothing else). Embeddings are cached in
`cache/` (not committed), keyed by model revision and text, so a re-run embeds only new texts.
"""
import csv
import gzip
import hashlib
import io
import json
import os
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
MODEL = "sentence-transformers/all-mpnet-base-v2"
REVISION = "e8c3b32edf5434bc2275fc9bab85f82640a19130"
CUTOFF = 0.5
SENSITIVITY = {"none": None, "0.7": 0.7}
CUTOFFS = {"0.5": 0.5, **SENSITIVITY}
BATCH = 64
THREADS = 4


def load_concepts(path=None):
    """[{uri, type, label, alt: [..], description}] in URI order."""
    path = path or next(HERE.glob("esco_skills_*_en.csv.gz"))
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in sorted(rows, key=lambda r: r["conceptUri"]):
        alt = [a.strip() for a in r["altLabels"].split("\n") if a.strip()]
        out.append({"uri": r["conceptUri"], "type": r["skillType"], "label": r["preferredLabel"].strip(), "alt": alt,
                    "description": r["description"].strip()})
    return out


def label_table(concepts):
    """Parallel lists: label text, index of its concept. Preferred label first, then alternatives in file order."""
    texts, owner = [], []
    for i, c in enumerate(concepts):
        for t in [c["label"], *c["alt"]]:
            texts.append(t)
            owner.append(i)
    return texts, np.array(owner, dtype=np.int32)


def link_scores(sims_best, cutoff):
    """True where a best similarity reaches the cutoff (None = no cutoff: always linked)."""
    sims_best = np.asarray(sims_best, dtype=float)
    if cutoff is None:
        return np.ones(sims_best.shape, dtype=bool)
    return sims_best >= cutoff


class Embedder:
    """all-mpnet-base-v2 with an on-disk cache per text (sha1 of the text -> row of a float32 store)."""

    def __init__(self, cache_dir=CACHE, model=MODEL, revision=REVISION):
        self.cache_dir, self.model_name, self.revision = Path(cache_dir), model, revision
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        tag = hashlib.sha1(f"{model}@{revision}".encode()).hexdigest()[:10]
        self.index_path = self.cache_dir / f"emb_{tag}.index.json"
        self.store_path = self.cache_dir / f"emb_{tag}.f32"
        self.index = json.loads(self.index_path.read_text()) if self.index_path.exists() else {}
        self._model = None

    def model(self):
        if self._model is None:
            import torch
            torch.set_num_threads(THREADS)
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, revision=self.revision, device="cpu")
        return self._model

    @staticmethod
    def key(text):
        return hashlib.sha1(text.encode("utf-8")).hexdigest()

    def embed(self, texts, progress=False):
        """float32 (len(texts), 768), L2-normalised."""
        texts = [t.strip() for t in texts]
        keys = [self.key(t) for t in texts]
        todo = sorted({(k, t) for k, t in zip(keys, texts) if k not in self.index})
        if todo:
            m = self.model()
            with open(self.store_path, "ab") as f:
                for a in range(0, len(todo), 4096):
                    part = todo[a:a + 4096]
                    vec = m.encode([t for _, t in part], batch_size=BATCH, normalize_embeddings=True,
                                   convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
                    start = os.path.getsize(self.store_path) // (768 * 4)   # rows already stored
                    f.write(vec.tobytes())
                    f.flush()
                    os.fsync(f.fileno())
                    for j, (k, _) in enumerate(part):
                        self.index[k] = start + j
                    self.index_path.write_text(json.dumps(self.index))
                    if progress:
                        print(f"  embedded {a + len(part)}/{len(todo)} new texts", flush=True)
        store = np.memmap(self.store_path, dtype=np.float32, mode="r").reshape(-1, 768)
        return np.asarray(store[[self.index[k] for k in keys]])


class Linker:
    def __init__(self, concepts, embedder):
        self.concepts = concepts
        self.label_texts, self.owner = label_table(concepts)
        self.embedder = embedder
        self.L = embedder.embed(self.label_texts, progress=True)

    def best(self, texts, chunk=256):
        """For each text: (concept index, best label index, cosine) of its most similar label."""
        E = self.embedder.embed(texts)
        ci, li, sc = np.zeros(len(texts), np.int32), np.zeros(len(texts), np.int32), np.zeros(len(texts), np.float32)
        for a in range(0, len(texts), chunk):
            S = E[a:a + chunk] @ self.L.T
            j = S.argmax(axis=1)
            li[a:a + chunk] = j
            sc[a:a + chunk] = S[np.arange(len(j)), j]
            ci[a:a + chunk] = self.owner[j]
        return ci, li, sc
