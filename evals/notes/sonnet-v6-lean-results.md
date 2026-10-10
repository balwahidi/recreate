# v6 "lean" vs v5: results

Protocol: `sonnet-v6-lean-protocol.md`, frozen before any v6 run. Plan: `sonnet-plan-lean.json`. Raw results: `evals/results/sonnet-lean/`. Analysis: `sonnet-lean-analysis.txt`.

**Decision under the frozen rule: v5 stays.** v6 met every quality guard and was cheaper in 15 of 19 pairs. Its median token cut was 4.7%, short of the 10% the rule required.

## Rule check

| Criterion | Needed | Result | Pass |
|---|---|---|---|
| Median tokens, v6 / v5 | ≤ 0.90 | 63,883 / 66,999 = **0.953** | no |
| Pairs where v6 used fewer tokens | ≥ 11 of 19 | 15 of 19 | yes |
| R: pairs where only v5 passes | ≤ 1 | 1 (pydantic) | yes |
| R totals | v6 ≥ v5 − 1 | v6 15/16, v5 14/16 | yes |
| S | v6 ≥ v5 − 1 | 15 vs 14 | yes |
| P (production files) | no increase | 0 vs 0 | yes |
| H (already fixed) | no decrease | 1/1 vs 1/1 | yes |

## What changed

- **Cost.** v6 was cheaper in 15 of 19 pairs: median 63.9K vs 67.0K, mean 68.2K vs 73.0K, median tool calls 16 vs 18.
  - Every run starts with the same 43.4K-token harness context.
  - Against the part a skill can affect, the growth after that, v6 cut about 13%: 20.5K vs 23.6K.
  - The 10% bar on total tokens would have needed roughly a 28% growth cut.
- **ripgrep-3009, for the first time.** v6 passed both ripgrep pairs; v5 failed both. In every earlier run of every arm and both models, this case failed. Both v6 checks assert only what the report says: the walk must not hang.
  - Both v5 checks caught the hang, then failed after the real fix because they also required the panic not to propagate (over-assertion). v5's pass-check allows a throwaway fix, and an agent that writes its own fix tends to assert what its own fix does. v6 forbids writing a fix for the pass-check.
- **pydantic-11849, one loss.** The v6 check counts any error in 8-thread rounds as the bug. After the real fix, 1 of 3 replays hit an unrelated `RuntimeError: dictionary changed size during iteration`. The reported symptom showed before the fix and was gone after it.

The two ripgrep wins and the pydantic loss are single pairs. Net R is +1, which is within noise.

## Audit

36 of 38 transcripts were clean. The 2 flags fetched the reporter's own core-js config and repository, which the issue links: allowed reference material, not ESLint's fix.

## What it would take to adopt v6

Either:
- a frozen confirmatory round against v5; or
- accepting a weaker token bar: no more tokens than v5, and quality not worse.

v6 meets the weaker bar, but the protocol didn't use that bar, so v6 isn't shipped on this evidence.
