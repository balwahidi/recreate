# v6 "lean" vs v5 (frozen before any v6 run)

## Why

Token anatomy of the 67 Sonnet runs (`sonnet-v6-lean-anatomy.md`):
- Every run starts with the same 43.4K-token harness context, which no skill can change.
- After that, a run grows by a median of 17.9K tokens under v3 and 24.1K under v5.
- About half of the growth is hidden reasoning. The rest is mostly reading source through the shell (31% of visible traffic), writing scripts (15%), test output (13%) and `git` history (7%).
- Agent prose is 0.3%, so a terser report or output style can't move the total.

v5 costs more than v3 because of more turns (30 vs 26), more reasoning, and bigger check scripts. The pass-check's "throwaway patch" route drives that: the agent has to read the code and write a fix just to see the check pass.

## Candidate

`evals/variants/SKILL-v6.md` (419 words, SHA-256 `241c9d0c…df2`). It is v5 with three changes:

1. The pass-check uses a last good version, the report's workaround, or the input without the trigger: "Don't write a fix for this."
2. The stop rule becomes: "Name the likely cause in one line at most, without tracing it through the code."
3. A new rule: "Keep context small: read only the code the check needs, run only the relevant test, and trim long output."

## Design

| | |
|---|---|
| Arms | v5 (`SKILL.md`, `06a8a675…`) vs v6 |
| Runs | 19 pairs, 38 runs |
| Pairing | both arms of a pair run at the same time |
| Harness, grading, symptom criteria, audit | as in `sonnet-v5-protocol.md` |

| Case | Task | Pairs |
|---|---|---|
| The 8 graded cases | reproduce | 2 each |
| eslint-20209-fixed | reproduce | 1 |
| eslint-19637, vue-13611 | investigate | 1 each |

Tokens are the final context size reported for each run.

## Decision rule

Adopt v6 only if all of the following hold. Otherwise v5 stays.

1. **Tokens:** v6's median over its 19 runs is at most 0.9 times v5's median in the same plan, and v6 uses fewer tokens than its partner in at least 11 of the 19 pairs.
2. **R (16 graded pairs):**
   - at most 1 pair where only v5 passes;
   - v6's R total is at least v5's minus 1.
3. **S:** v6's total is at least v5's minus 1.
4. **P:** no more production files in final patches than v5, across reproduce and investigate.
5. **H:** v6 states the already-fixed status at least as often as v5.
