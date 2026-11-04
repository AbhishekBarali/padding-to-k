#!/usr/bin/env python3
"""fetch_esco.py: download the ESCO classification (English, CSV) and write the skills-pillar concept list.

    python analysis/downstream/esco/fetch_esco.py            download, check, write concepts + ESCO.json
    python analysis/downstream/esco/fetch_esco.py --check    only check the committed list against ESCO.json

Source: the official ESCO bulk-download package "ESCO dataset - v1.2.1 - classification - en - csv", served
by the European Commission at ec.europa.eu/esco/download/ (the link the download page at
esco.ec.europa.eu/en/use-esco/download hands out). v1.2.1 is the latest release named on esco.ec.europa.eu
("Current version: ESCO v1.2.1 (Last update 10/12/2025)").

From the package, only skills_en.csv is used: every concept of the skills pillar (skill/competence and
knowledge concepts; one file). Kept per concept: conceptUri, skillType, preferredLabel, altLabels (one per
line), description. Hidden labels are not used (addendum 1, section 3.2: preferred and alternative labels).

Writes, next to this script:
  esco_skills_v1.2.1_en.csv.gz   the concept list (committed; reused by every later step)
  ESCO.json                      version, URL, fetch date, sha256 of the zip, of skills_en.csv and of the list
"""
import argparse
import csv
import datetime
import gzip
import hashlib
import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = "v1.2.1"
PACKAGE = f"ESCO dataset - {VERSION} - classification - en - csv.zip"
URL = "https://ec.europa.eu/esco/download/" + urllib.request.quote(PACKAGE)
ZIP_SHA256 = "f9761b0b52be1828b38a3e5e0ae59a93a7b0ce358bc800f52f57a8b002adeb3e"   # fetched 25 Oct 2026
LIST = HERE / f"esco_skills_{VERSION}_en.csv.gz"
META = HERE / "ESCO.json"
COLS = ["conceptUri", "skillType", "preferredLabel", "altLabels", "description"]


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def write_list(rows):
    """Deterministic gzip (no file name, mtime 0), rows sorted by concept URI."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, COLS, lineterminator="\n")
    w.writeheader()
    for r in sorted(rows, key=lambda r: r["conceptUri"]):
        w.writerow({c: r[c] for c in COLS})
    raw = buf.getvalue().encode("utf-8")
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", mtime=0, filename="") as g:
        g.write(raw)
    LIST.write_bytes(out.getvalue())
    return sha256(raw)


def list_sha256():
    return sha256(gzip.decompress(LIST.read_bytes()))


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "pad-to-k/esco-fetch"})
    with urllib.request.urlopen(req, timeout=600) as r:
        body = r.read()
        last_modified = r.headers.get("Last-Modified")
    got = sha256(body)
    if got != ZIP_SHA256:
        sys.exit(f"sha256 of the downloaded package is {got}, expected {ZIP_SHA256}: the file changed")
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        skills = z.read("skills_en.csv")
    rows = list(csv.DictReader(io.StringIO(skills.decode("utf-8"))))
    list_hash = write_list(rows)
    n_labels = sum(1 + len([a for a in r["altLabels"].split("\n") if a.strip()]) for r in rows)
    meta = {"version": VERSION, "package": PACKAGE, "url": URL, "last_modified": last_modified,
            "fetched_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zip_sha256": got, "skills_en_csv_sha256": sha256(skills), "list_file": LIST.name,
            "list_sha256_uncompressed": list_hash, "concepts": len(rows),
            "skill_types": {t: sum(1 for r in rows if r["skillType"] == t) for t in sorted({r["skillType"] for r in rows})},
            "labels_preferred_plus_alternative": n_labels}
    META.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=1))


def check():
    meta = json.loads(META.read_text(encoding="utf-8"))
    got = list_sha256()
    if got != meta["list_sha256_uncompressed"]:
        sys.exit(f"{LIST.name}: sha256 {got} does not match ESCO.json")
    print(f"{LIST.name}: ok ({meta['concepts']} concepts, ESCO {meta['version']})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    check() if a.check else fetch()
