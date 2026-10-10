"""Show graded runs for blind adjudication: command, verdict and log excerpts, no arm.

usage: blind.py <results-dir-name> [label-substring ...]
Labels are <case>__<run_id>__<task>; the arm lives only in /work/plan-*.json.
"""
import json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
run, filters = sys.argv[1], sys.argv[2:]
grade_dir = ROOT / "evals/results" / run / "grade"
labels = sorted(p.stem for p in grade_dir.glob("*.json") if not filters or any(f in p.stem for f in filters))
random.shuffle(labels)


def excerpt(path, limit=1800):
    if not path.exists():
        return "(no log)"
    text = path.read_text(errors="replace")
    return text if len(text) <= limit else text[: limit // 2] + "\n[...]\n" + text[-limit // 2:]


for label in labels:
    g = json.loads((grade_dir / f"{label}.json").read_text())
    res = json.loads((ROOT / "evals/results" / run / f"{label}.json").read_text())
    print("=" * 100)
    print(f"{label}  verdict={g['verdict']} pre={g.get('pre')} post={g.get('post')}")
    print(f"run_command: {res.get('run_command', '')[:400]}")
    for side in ("pre", "post"):
        print(f"--- {side}")
        print(excerpt(grade_dir / f"{label}.{side}.log"))
