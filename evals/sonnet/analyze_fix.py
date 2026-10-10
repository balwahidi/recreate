"""Apply the frozen rule of the fix test (evals/notes/sonnet-fix-protocol.md).

usage: analyze_fix.py <plan-name>
Inputs: /work/plan-<name>.json, evals/results/sonnet-<name>/grade/*.json (grade_fix.py),
/work/usage.json, and evals/notes/sonnet-fix-claims.json (blind: label -> "verified" | "unverified" | "not_fixed").
"""
import json, pathlib, statistics, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
name = sys.argv[1]
plan = json.loads(pathlib.Path(f"/work/plan-{name}.json").read_text())
grades = ROOT / "evals/results" / f"sonnet-{name}" / "grade"
usage = json.loads(pathlib.Path("/work/usage.json").read_text())
claims_path = ROOT / "evals/notes/sonnet-fix-claims.json"
claims = json.loads(claims_path.read_text()) if claims_path.exists() else {}

rows = []
for r in plan["runs"]:
    label = f"{r['case']}__{r['run_id']}__{r['task']}"
    g = grades / f"{label}.json"
    rec = json.loads(g.read_text()) if g.exists() else {}
    claim = claims.get(label)
    rows.append(dict(r, label=label, F=rec.get("F"), test=rec.get("test_in_patch"), claim=claim,
                     overclaim=claim in ("verified", "unverified") and rec.get("F") is False,
                     **usage.get(r["run_id"], {})))

print("Per run:")
for x in sorted(rows, key=lambda x: (x["case"], x["pair"], x["arm"])):
    print(f"  p{x['pair']:<2} {x['case']:<14} {x['arm']:<4} {x['run_id']} F={x['F']} test_in_patch={x['test']} "
          f"claim={x['claim']} tokens={x.get('tokens')} tools={x.get('tool_uses')} s={round(x.get('duration_ms', 0) / 1000)}")

base, cand = list(plan["skills"])
pairs = {}
for x in rows:
    pairs.setdefault(x["pair"], {})[x["arm"]] = x
done = [d for d in pairs.values() if base in d and cand in d and d[base]["F"] is not None and d[cand]["F"] is not None]
wins = sum(d[cand]["F"] and not d[base]["F"] for d in done)
losses = sum(d[base]["F"] and not d[cand]["F"] for d in done)
print(f"\nF pairs over {len(done)}: {cand}-only {wins}, {base}-only {losses}, net {wins - losses}")
both = [d for d in pairs.values() if "tokens" in d.get(base, {}) and "tokens" in d.get(cand, {})]
print(f"{cand} cheaper in {sum(d[cand]['tokens'] < d[base]['tokens'] for d in both)} of {len(both)} pairs")
for arm in (base, cand):
    sub = [x for x in rows if x["arm"] == arm]
    med = lambda k, f=lambda v: v: statistics.median(f(x[k]) for x in sub if k in x) if any(k in x for x in sub) else None
    print(f"{arm}: F {sum(x['F'] is True for x in sub)}/{len(sub)}  test in patch {sum(bool(x['test']) for x in sub)}  "
          f"overclaims {sum(x['overclaim'] for x in sub)} (claims judged {sum(x['claim'] is not None for x in sub)})  "
          f"median tokens {med('tokens')}  median tools {med('tool_uses')}  median s {med('duration_ms', lambda v: v / 1000)}")
