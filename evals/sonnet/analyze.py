"""Apply the frozen decision rule (evals/notes/sonnet-v5-protocol.md) to a finished plan.

usage: analyze.py <plan-name>
Inputs: /work/plan-<name>.json, evals/results/sonnet-<name>/ (results and grade/),
/work/usage.json, and evals/notes/sonnet-adjudication.json (blind verdicts:
label -> {"symptom": bool, "over_assertion": bool, "note": str}, plus
"H:<run_id>" -> bool for the already-fixed case).
"""
import json, pathlib, re, statistics, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
name = sys.argv[1]
plan = json.loads(pathlib.Path(f"/work/plan-{name}.json").read_text())
res_dir = ROOT / "evals/results" / f"sonnet-{name}"
usage = json.loads(pathlib.Path("/work/usage.json").read_text())
adj = json.loads((ROOT / "evals/notes/sonnet-adjudication.json").read_text())
cases = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}


def label(r):
    return f"{r['case']}__{r['run_id']}__{r['task']}"


def verdict(r):
    g = res_dir / "grade" / f"{label(r)}.json"
    return json.loads(g.read_text())["verdict"] if g.exists() else None


def prod_files(r):
    path = res_dir / f"{label(r)}.json"
    if not path.exists():
        return []
    patch = json.loads(path.read_text()).get("patch", "")
    files = []
    # A file counts only if some hunk falls outside an inline Rust `mod tests` block.
    for chunk in re.split(r"(?m)^(?=diff --git )", patch):
        m = re.match(r"diff --git a/(\S+)", chunk)
        if m and any("mod tests" not in h for h in re.findall(r"(?m)^@@[^\n]*", chunk)):
            files.append(m.group(1))
    fix = cases[r["case"]]["fix_prod_files"]
    if fix == "ALL_NON_TEST":
        return [f for f in files if f.endswith(".go") and not f.endswith("_test.go")]
    return [f for f in files if f in fix]


rows = []
for r in plan["runs"]:
    v = verdict(r)
    a = adj.get(label(r), {})
    row = dict(r, verdict=v, prod=prod_files(r), **usage.get(r["run_id"], {}))
    row["R"] = v == "fail_to_pass" and a.get("symptom") is True
    row["S"] = v in ("fail_to_pass", "pass_to_fail") and a.get("symptom") is True
    row["A"] = a.get("over_assertion") is True
    row["H"] = adj.get(f"H:{r['run_id']}")
    rows.append(row)

arms = plan["skills"].keys()
print("Per run:")
for row in sorted(rows, key=lambda x: (x["case"], x["task"], x["pair"], x["arm"])):
    print(f"  p{row['pair']:<2} {row['case']:<19} {row['task']:<11} {row['arm']:<4} {row['run_id']} "
          f"{str(row['verdict']):<24} R={int(row['R'])} S={int(row['S'])} A={int(row['A'])} "
          f"H={row['H']} prod={row['prod']} tokens={row.get('tokens')} tools={row.get('tool_uses')} "
          f"s={round(row.get('duration_ms', 0) / 1000)}")

graded = [x for x in rows if x["task"] == "reproduce" and cases[x["case"]]["fix"]]
pairs = {}
for x in graded:
    pairs.setdefault(x["pair"], {})[x["arm"]] = x
wins = losses = 0
for p, d in sorted(pairs.items()):
    if "v3" in d and "v5" in d:
        wins += d["v5"]["R"] and not d["v3"]["R"]
        losses += d["v3"]["R"] and not d["v5"]["R"]
print(f"\nR pairs: v5-only {wins}, v3-only {losses}, net {wins - losses} over {len(pairs)} pairs")
for arm in arms:
    sub = [x for x in rows if x["arm"] == arm]
    g = [x for x in graded if x["arm"] == arm]
    toks = [x["tokens"] for x in sub if "tokens" in x]
    print(f"{arm}: R {sum(x['R'] for x in g)}/{len(g)}  S {sum(x['S'] for x in g)}/{len(g)}  "
          f"A {sum(x['A'] for x in g)}  P {sum(bool(x['prod']) for x in sub if x['task'] in ('reproduce', 'investigate'))}  "
          f"H {sum(x['H'] is True for x in sub)}/{sum(x['H'] is not None for x in sub)}  "
          f"median tokens {statistics.median(toks) if toks else None}  "
          f"median tools {statistics.median([x['tool_uses'] for x in sub if 'tool_uses' in x]) if toks else None}  "
          f"median s {statistics.median([x['duration_ms'] / 1000 for x in sub if 'duration_ms' in x]) if toks else None}")
