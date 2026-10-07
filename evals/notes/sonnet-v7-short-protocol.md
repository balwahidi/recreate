# v7 "short" vs v5 (frozen before any v7 run)

## Why

v5 is 383 words. Only some of it has measured effects:
- no production edits before a reproduction;
- only the reported symptom counts, and already-fixed reports are named as such;
- "The check": exit status, assert only the report, pass once.

The report format, with its status menu, ten named fields and "Not reproduced" template, has no measured effect.

v7 keeps the measured rules in five lines and replaces the report format with one sentence. It also takes the pass-check from v6: see it pass without writing a fix. In the v6 test that wording passed ripgrep-3009 for the first time.

## Arms

| Arm | File | Words | SHA-256 |
|---|---|---|---|
| v5 | `SKILL.md` | 383 | `06a8a675…7619` |
| v7 | `evals/variants/SKILL-v7.md` | 202 | `5c454b0c…3f7d` |

## Runs

20 pairs, 40 runs:

| Case | Task | Pairs |
|---|---|---|
| The 8 graded cases | reproduce | 2 each |
| eslint-20209-fixed (honesty is the main risk of the cuts) | reproduce | 2 |
| eslint-19637, vue-13611 | investigate | 1 each |

The harness, grading, symptom criteria, blind review and audit are as before.

## Decision rule

This is the user's bar: quality no worse, and no more tokens. Adopt v7 only if all of the following hold. Otherwise v5 stays.

1. **R (16 graded pairs):**
   - at most 1 pair where only v5 passes;
   - v7's total is at least v5's minus 1.
2. **S:** v7's total is at least v5's minus 1.
3. **P:** no more production files in final patches than v5, across reproduce and investigate.
4. **H:** v7 states the already-fixed status at least as often as v5 (2 pairs).
5. **Tokens:** v7's median over its 20 runs is at most v5's median in the same plan.
