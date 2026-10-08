# v8 on the cases v7 failed: results

Protocol: `sonnet-fix2-protocol.md`, frozen before any run. Raw results: `evals/results/sonnet-fix2/`.

**Decision under the frozen rule: v7 stays.** v8 fixed 3 of 6; the bar was 5 of 6.

| Case | v8 | v7 (fix test) | No skill (fix test) |
|---|---|---|---|
| ripgrep-3009 | **3/3** | 1/2 | 2/2 |
| vue-13611 | 0/3 | 0/2 | 1/2 |
| Median tokens | 100.5K | 95.5K on these cases | |

## What happened

- **ripgrep:** the new line did what it was meant to. All 3 v8 fixes cover the panic in the visitor builder as well as the reported visitor panic. That second path is the one a v7 run missed.
- **vue:** all 3 v8 runs again fixed only compiled slots. Each kept `_`-prefixed keys ignored in render-function slots, because an existing Vue test asserts it (`expect(slots).not.toHaveProperty('_inner')`). Upstream's fix deliberately changed that behaviour and rewrote the test.
  - Across every arm, 6 of 7 vue runs made the same choice.
  - So vue measures whether an agent will overturn a tested contract, not whether it misses a path. A "look for other paths" line can't change that, and arguably shouldn't.

## Reading

The evidence points one way: v8 fixes the "missed a second path" failure on the one case where that failure is a genuine bug. But that rests on 3 runs on a case the line was written for, and the frozen rule wasn't met. v8 stays a variant (`evals/variants/SKILL-v8.md`), and `SKILL.md` stays v7.
