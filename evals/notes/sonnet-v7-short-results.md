# v7 "short" vs v5: results

Protocol: `sonnet-v7-short-protocol.md`, frozen before any v7 run, plus an addendum written mid-run. Plan: `sonnet-plan-short.json`. Raw results: `evals/results/sonnet-short/`. Analysis: `sonnet-short-analysis.txt`. Audit: `sonnet-short-audit.txt`.

**Decision under the frozen rule: v7 is adopted.** It passed every criterion. v7 is 202 words against v5's 383.

## Rule check

| Criterion | Needed | v5 | v7 | Pass |
|---|---|---|---|---|
| R: pairs where only v5 passes | ≤ 1 | | 0 (v7-only: 2) | yes |
| R totals (16 graded pairs) | v7 ≥ v5 − 1 | 14/16 | **16/16** | yes |
| S | v7 ≥ v5 − 1 | 14/16 | 16/16 | yes |
| P: production files in final patches (reproduce + investigate) | no increase | 0 | 0 | yes |
| H: already-fixed status stated | no decrease | 2/2 | 2/2 | yes |
| Median tokens over 20 runs | v7 ≤ v5 | 73,180 | **63,789** | yes |

Without the two ripgrep pairs (see the addendum and "Cross-run interference" below), every criterion still holds:
- R is 14/14 for both arms.
- Median tokens are 62,628 for v7 and 69,828 for v5.

So the original runs stand.

## What changed

- **Quality.** Every v5 miss came from one cause, which also caused v5's misses in the v6 test:
  - Both v5 ripgrep-3009 checks caught the hang. After the real fix they still failed, on `should_panic` expecting the message `oops!`. The blind reviewer marked both as over-assertion.
  - Both v7 checks assert only that the walk returns.
  - Across the v6 and v7 tests, wording that rules out writing a fix for the pass-check is now 4/4 on ripgrep. v5's throwaway-fix wording is 0/4.
  - Every other case was 2/2 in both arms. The blind reviewer found the reported symptom in all 32 pre logs.
- **Cost.**
  - Median tokens were 12.8% lower, and v7 was cheaper in 14 of 20 pairs. The mean cut is smaller: 69.5K vs 73.8K (5.9%).
  - Against the growth after the fixed 43.4K harness context, the cut is about a third: 20.4K vs 29.8K at the median.
  - Median tool calls were 15.5 vs 21, and median wall time was 136 s vs 257 s.
- **Reports didn't get thinner.** v7 has no report template, only "Report the status, the command, and what you saw."
  - v7 final messages were about as long as v5's: median 336 words vs 318.
  - All 4 already-fixed runs led with an already-fixed status.
  - All 12 runs on the three flaky cases (urfave, pydantic, ripgrep) stated a failure rate.

## Cross-run interference

The four ripgrep runs ran at the same time on one machine, and their test binaries share a name (`ignore-ecb739db799020ac`). All four cleared hung tests with a `pkill -f` or `pkill -x` pattern that matches every run's binary, not just their own. 393bff8e2a also attached gdb to the first matching PID.

Three transcripts show other runs' test processes in the process list. 36df0aaebf's report says its kill may have hit bd75270ed7 (v5). Both arms did this: two v7 runs and two v5 runs.

Grading replays each patch alone afterwards, so verdicts are unaffected. Both v5 misses are the same `should_panic` over-assertion v5 showed in the v6 test, with no ripgrep interference involved there. The handling (apply the rule with and without the ripgrep pairs, rerun if they differ) was fixed before the last two ripgrep runs finished.

Future plans should run cases with hang-prone tests one at a time.

## Audit

36 of 40 transcripts were clean.
- 3 flags were fetches of the reporter's own core-js config, which the issue links. That is allowed reference material, not ESLint's fix.
- 1 flag is 36df0aaebf's report naming the other run (see above).

Blind review was done by a fresh agent that saw only the shuffled logs and the pre-written symptom criteria (`sonnet-symptoms.md`), not the plan or arm mapping. One verdict, where the note said the directive was inferred, was checked against the full log: the two reports are exactly at the two `'use strict'` directives.

## Limits

- R was near ceiling for both arms, so this test can only rule out a large quality loss on these cases. Its one discriminating case, ripgrep, agrees with the v6 test.
- The v5 median in this plan, 73.2K, is higher than in the v6 plan, 67.0K. Run-to-run variance is several thousand tokens, and the token result is a 14-of-20 pair split, not a large effect.
- These cases didn't exercise the parts of v5 that v7 compressed most:
  - the "Not reproduced" template;
  - the status menu;
  - the simulated-environment status line.

  v7 keeps one-line rules for each.
