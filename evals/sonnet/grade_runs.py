"""Replay-grade a Sonnet run with evals/grade.py and the per-case adjustments below.

usage: python3 evals/sonnet/grade_runs.py <results-dir-name> [label-substring ...]
"""
import json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import grade  # noqa: E402
from cases import RUN_PREFIX  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
INSTALL = {
    "eslint": "npm install --ignore-scripts --no-audit --no-fund",
    "vue": "pnpm i --frozen-lockfile",
    "ts": "npm ci --ignore-scripts --no-audit --no-fund",
    "urfave": "go mod download",
    "pydantic": "source .venv/bin/activate && pip install -q -e .",
}
MANIFESTS = re.compile(r"^diff --git a/(\S*/)?(package\.json|package-lock\.json|pnpm-lock\.yaml|go\.mod|go\.sum|pyproject\.toml)\b", re.M)
grade.BUILD = {"ts-60573": "npx hereby local"}
grade.POST_EXTRA = {"urfave-cli-2176": "upstream_test.patch"}


def main():
    run, filters = sys.argv[1], sys.argv[2:]
    cases = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}
    res_dir = ROOT / "evals/results" / run
    out_dir = res_dir / "grade"
    out_dir.mkdir(exist_ok=True)
    for path in sorted(res_dir.glob("*.json")):
        label = path.stem
        cid = label.split("__")[0]
        if cid not in cases or (filters and not any(f in label for f in filters)):
            continue
        case = cases[cid]
        grade.clear_grade_files(out_dir, label)
        result = json.loads(path.read_text())
        if "error" in result:
            record = {"label": label, "case": cid, "verdict": "agent_error", "error": result["error"]}
        elif not case["fix"]:
            continue
        elif not result.get("run_command"):
            record = {"label": label, "case": cid, "verdict": "no_reproduction_artifact"}
        else:
            # Reinstall dependencies only when the agent's patch changes a manifest.
            grade.SETUP = {}
            if MANIFESTS.search(result.get("patch") or ""):
                grade.SETUP[cid] = INSTALL[cid.split("-")[0]]
            result = dict(result, run_command=RUN_PREFIX.get(cid, "") + result["run_command"])
            record = grade.grade(case, label, result, out_dir)
        (out_dir / f"{label}.json").write_text(json.dumps(record, indent=2))
        print(f"{label}: {record['verdict']} pre={record.get('pre')} post={record.get('post')}", flush=True)


if __name__ == "__main__":
    main()
