# v8 on the cases v7 failed (frozen before any v8 run)

## Why

In the fix test (`sonnet-fix-results.md`), v7 fixed 7 of 10, against 9 of 10 with no skill. Both v7 losses, and 3 of v7's misses, fixed only the path their reproduction exercised:
- vue-13611: render-function slots;
- ripgrep-3009: a panic in the visitor builder.

v7's fix path reads only "otherwise continue from the check".

## The change (v7 → v8)

The last bullet. v7 says:

> Leave production code alone until the check fails. If the task is only to reproduce, stop there; otherwise continue from the check.

v8 says:

> Leave production code alone until the check fails. If the task is only to reproduce, stop there. When fixing, fix the cause, not just the path your check exercises: find the other ways to reach that cause and cover them too. A passing check doesn't mean the fix is complete.

- v8: `evals/variants/SKILL-v8.md`, 230 words, SHA-256 `a6cb0a46…fee4f`.
- Nothing else changes. Reproduce-only tasks stop before the new text.

## Runs

The user asked to run only the cases Recreate failed:
- vue-13611, 3 runs of v8;
- ripgrep-3009, 3 runs of v8.

Same prompt as the fix test ("Fix this bug.", no request for a demonstrating command). Same validated graders (`grade_fix.py`). ripgrep runs go one at a time.

The references come from the fix test on the same cases and graders:

| Arm | F on these cases | Median tokens on these cases |
|---|---|---|
| v7 | 1/4 | 95.5K |
| no skill | 3/4 | |

## Decision rule

v8 replaces v7 in `SKILL.md` only if both hold. Otherwise v7 stays.

1. **F:** v8 fixes at least 5 of 6.
2. **Tokens:** v8's median over its 6 runs is at most 110K, which is 1.15 × v7's 95.5K on these cases.

## Limits, stated in advance

- **The line was written after seeing these failures.** Passing here shows it fixes this failure mode on these cases. It doesn't show that it generalises. The high bar (5 of 6, against v7's 1 of 4) partly makes up for that.
- **Other cases aren't rerun.** The change adds text only to the fix path, so reproduce and investigate behaviour shouldn't move. Cost and correctness on the other three fix cases aren't retested here.
