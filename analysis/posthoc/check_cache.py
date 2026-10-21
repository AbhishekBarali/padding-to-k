"""POST HOC helper: confirm the scored cache matches the run folders (same source hash full_study_score uses)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "harness"), str(ROOT / "analysis")]
import full_study_score as fss
runs = Path(sys.argv[1]); cache = ROOT / "analysis/full/scored"
bad = 0
for meta in sorted(cache.glob("*.source.json")):
    m = json.loads(meta.read_text()); d = runs / m["run_id"]
    ok = d.exists() and fss.source_hash(d) == m["source"] and (cache / f"{m['run_id']}.entries.csv.gz").exists()
    bad += not ok
    if not ok: print("STALE", m["run_id"])
print("checked", len(list(cache.glob('*.source.json'))), "stale", bad)
