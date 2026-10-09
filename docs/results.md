# Results

The shipped skill is reproduction-only: v7's measured rules, with its hand-off to fixing replaced by "don't fix it", because the fix tests below showed no gain. v7 (202 words) replaced v5 (383 words) after a frozen Sonnet comparison; see section 0. Sections 1 to 7 describe the earlier v0 to v3 runs. Those all use one harness and one model, Devin sessions, with identical prompts in both arms (see `methodology.md`). Raw outputs and replay logs are in `evals/results/<run>/`, and decisions are recorded in `evals/notes/baseline-dev-v1.md`.

## 0. Sonnet evaluations of v5 and v7

**v7 "short" (current).** v7 keeps v5's measured rules in five lines and drops the report template, the status menu and the "Not reproduced" form. Its pass-check rules out writing a fix. It ran against v5 in 20 frozen, paired runs per arm and passed every criterion of the frozen rule:

| | v5 | v7 |
|---|---|---|
| R (fails before the fix, passes after, reported symptom) | 14/16 | 16/16 |
| Pairs won | 0 | 2 (14 ties) |
| Production files in final patches | 0 | 0 |
| Already-fixed status stated | 2/2 | 2/2 |
| Median tokens (20 runs) | 73,180 | 63,789 (cheaper in 14 of 20 pairs) |

- Both v5 misses were ripgrep-3009 over-assertions on the panic message, the same failure v5 showed in the v6 test. Wording that forbids a throwaway fix has now passed ripgrep 4 of 4 times, and v5 0 of 4.
- The four concurrent ripgrep runs killed each other's hung tests by process name, and both arms did it. The pre-registered check without those pairs gives the same decision.
- Details are in `evals/notes/sonnet-v7-short-results.md`.

**Fix test: v7 vs no skill on "Fix this bug."** 5 cases, 2 pairs each. Fixes were graded by upstream's own hidden tests plus existing neighbouring tests, and every grader was validated against the checkout and the upstream fix first.

| | No skill | v7 |
|---|---|---|
| Fix correct | 9/10 | 7/10 |
| Pairs won | 2 | 0 (8 ties) |
| Before/after check cited (blind) | 9/10 | 10/10 |
| Regression test added | 10/10 | 10/10 |
| Median tokens | 80.6K | 86.4K |

- Under the frozen rule this reads "Recreate fixes worse". It rests on 2 pairs.
- Both v7 losses fixed the reproduced path and missed a sibling one: vue's render-function slots, and ripgrep's panic in the visitor builder.
- Without the skill, Sonnet already reproduces first and adds a regression test when fixing.
- Details are in `evals/notes/sonnet-fix-results.md`.

**v5** (the rest of this section).

v5 is v3 plus a "The check" section: one command that exits non-zero while the bug is present and zero once it's fixed, that asserts only the reported behavior, and that has been seen passing once. The evaluated agents were Sonnet Agent-tool subagents. Each graded reproduction was replayed against the real upstream production fix. Full results, every miss and the audit are in `evals/notes/sonnet-v5-results.md`; the protocols were frozen before their runs.

| | No skill | v3 | v5 |
|---|---|---|---|
| Fails before the fix, passes after, with the reported symptom (main + confirmatory) | 4/8 | 17/24 | 22/24 |
| Head-to-head pairs won (v3 vs v5) | | 0 | 5 (19 ties; sign test p = 0.0625) |
| Production files edited on "Look into this bug report." | 2/2 | 0/2 | 0/2 |
| Already-fixed report: status says already fixed | 0/1 | 2/2 | 2/2 |
| Median tokens per run | 64K | 61K | 64 to 68K |

- **Every arm found the bug every time.** The reported symptom was in the pre log and gone from the post log in 56 of 56 graded runs.
- **Every v3 miss was an exit-status failure:** a print-only script, `tsc` exiting 2 by design, or `; echo`.
- **v5's only misses were on ripgrep-3009.** The reporter's own `should_panic(expected = "oops!")` doesn't survive the real fix, which re-panics with a different message. Every arm hit that ceiling.
- **The main run alone was inconclusive under its frozen rule** (net +2). A frozen confirmatory round on eslint-19924 and ts-60573 then gave v5 8/8 vs v3 5/8, which cleared its rule.

**Token follow-up: v6 "lean", not adopted.** Every run starts with a fixed 43.4K-token harness context. Of the growth after that, about half is hidden reasoning and agent prose is 0.2%. So a terser output style can't move the cost; only doing less can.

v6 dropped the throwaway fix from the pass-check, stopped cause-tracing on reproduce tasks, and asked for small context. Results over 19 pairs:
- It was cheaper in 15 (median 63.9K vs 67.0K, a 4.7% cut).
- R was 15/16 vs 14/16. v6 passed ripgrep-3009 for the first time, and lost one pydantic pair to a check that counted an unrelated error.

Its frozen rule required a 10% median cut, so v5 stayed at the time. v7 later carried its no-fix pass-check forward. Details are in `evals/notes/sonnet-v6-lean-results.md`.

Clean runs: `baseline-dev-v1`, `baseline-dev-v2`, `treatment-dev-v0`, `holdout-v0`, `repeat-v0`, `ablation-v2b`, `holdout-v3b`, `simulated-v4`, `holdout-control-r`. `ablation-v2`, `holdout-v3` and `treatment-v1-probe` are excluded because they were contaminated through shared memory (see `methodology.md`).

## 1. Faithful reproduction, mechanical replay (primary metric)

On "Reproduce this bug" prompts, the reproduction must fail before the upstream fix and pass after it.

**Holdout**, 9 cases with an upstream fix. "Skill v0" is the frozen skill run before anyone looked at holdout results. "Skill v3" is the shipped skill. It ran after one rule (native tests) was removed partly because of what the v0 holdout run showed, so v3 is not an unseen-data estimate. Cases marked * had snapshots that leaked a maintainer's diagnosis (see `methodology.md`). Both arms saw the same text.

| Case | Control | Skill v0 | Skill v3 | Why the control's reproduction fails replay |
|---|---|---|---|---|
| eslint-19637 | 1/1 | 1/1 | 1/1 | |
| pytest-13312 | 1/1 | 1/1 | 1/1 | |
| vite-20705* | 1/1 | 1/1 | 1/1 | |
| vue-13611 | 1/1 | 1/1 | 1/1 | |
| eslint-19957 | 1/3 | 1/1 | 1/1 | Asserts literals beyond the report, which stay flagged after the fix. |
| pnpm-10290 | 1/3 | 1/1 | 1/1 | Recomputes the path via `@pnpm/config` instead of running the reported `pnpm store path`. |
| ts-60573* | 1/3 | 1/1 | 1/1 | One is a baseline test without its baseline files; another runs `tsc`, which exits non-zero by design. |
| pydantic-11849 | 0/3 | 0/1 | 1/1 | Counts any rare unrelated error as a failure (the v0 skill run has the same flaw). |
| ripgrep-3009 | (0/1) | (0/1) | (0/1) | Both arms: the wrapper exits 0 on a hang, and the assertion on the panic message is stricter than the fix. The hang itself reproduces before the fix and is gone after it. |

**Matched comparison** (run holdout-v0: one sample per case per arm, frozen v0, excluding ripgrep):

- **Control: 4 of 8.**
- **Skill v0: 7 of 8.**
- Without the two leaked cases: 3 of 6 vs 5 of 6.
- Also without pydantic-11849, whose body may have leaked through a later edit: 3 of 5 vs 5 of 5.

The Control column also counts two extra control samples per case (run holdout-control-r). They were drawn only on the four cases where the arms differed, so they aren't pooled into the comparison. What they show is that the control's failures there weren't one-offs: 3 of 8 extra samples passed.

Skill v3 passed 8 of 8 (6 of 6 without the leaked cases). The grader resets the checkout before the post side, and re-grading with that reset changed no verdict.

**Dev**, 4 cases with an upstream fix (eslint-19245, eslint-19924, urfave-cli-2176, vue-12294): every sample in every arm passes replay. That's control 8/8 and skill 8/8 across `baseline-dev-v1`, `treatment-dev-v0` and `ablation-v2b`.

## 2. False or substituted reproduction

| Case | Control | Skill (with the rule) | Skill without the rule |
|---|---|---|---|
| eslint-20209-fixed: the reported snippet already passes at the checkout | 0/6 say already fixed; all 6 report a related variant as "reproduced" | 5/5 | 2/2 (minimal) |
| eslint-19033-fixed: holdout, already fixed | 1/1 | 2/2 | — |
| eslint-18575-windows: Windows simulated on Linux, labelled in the status | 0/6 (mentioned in the body) | 6/6 | 3/4 (minimal, v4) |
| eslint-19818: behavior is as documented | 0/1 | 0/4 with the as-designed rule | — |

The as-designed rule had no effect and was removed.

## 3. Speculative production edits

| Prompt | Control | Skill |
|---|---|---|
| "Look into this bug report." Production files in the final patch | 9/10 | 0/15 (minimal 0/2) |
| "Fix this bug." Production edited before any reproduction ran | 2/2 | 0/4 (all still fixed the bug) |
| "Reproduce this bug." Production files in the final patch | 0 | 0 |

## 4. Flaky failures

On urfave-cli-2176 (a data race), runs that stated a rate: control 0/3, skill 3/3 (for example "9 out of 100,000 subtest runs"), minimal skill 1/2 (a coarse "5 of 5 runs"). All of these reproductions fail replay on 3 of 3 pre runs.

## 5. Not reproduced

No case's exact report failed to reproduce at both the checkout and the reporter's version, so the "Not reproduced" format was never used. The already-fixed status is the closest exercise of it. **This branch is untested by evals.**

## 6. Cost

- **Instructions:** 289 words. The draft was 352.
- **Report length,** median words: reproduce 312 control vs 295 skill; investigate 311 vs 286; fix 234 vs 263 (holdout-v0).
- **Session time,** median minutes within the same run: reproduce 2.7 vs 2.8; investigate 3.1 vs 2.0; fix 3.2 vs 3.9 (holdout-v0). Times across runs aren't comparable, because platform load varied.
- **Tokens per session:** not available. The harness didn't report usage.

## 7. Instruction ablation summary

| Instruction | Evidence | Kept? |
|---|---|---|
| Leave production code unchanged until reproduced | investigate 9/10 → 0/15 | yes |
| Exact steps; only the reported symptom counts | already-fixed substitution 6/6 → 0/5; matched holdout replay 4/8 → 7/8 with v0 (attribution not isolated) | yes |
| Try the reporter's version → already fixed | as above | yes |
| Call simulated conditions simulated | 6/6 with the rule, 3/4 without | yes (17 words) |
| Flaky: state a rate | 3/3 vs 1/2 (minimal) vs 0/3 | yes |
| Stop at reproduction unless asked for more | fix prompts still fixed, 4/4 | yes |
| Prefer the repository's native test mechanism | no measured effect | removed |
| Documented or tested intent → "Behaves as documented" | 0/4 clean runs changed | removed |
| General environment-parity guidance | no measured effect | removed |

## Verdict

The skill doesn't make the agent find bugs it otherwise misses: the control reproduced every reported symptom. What it changes:

- **Fewer speculative fixes.** On investigate and fix prompts, the agent no longer edits production code before reproducing.
- **Honest status** for already-fixed, simulated and flaky cases.
- **More faithful reproduction artifacts** on the holdout set: the frozen skill passes mechanical replay in 7 of 8 cases, the control in 4 of 8 (matched, one sample each).

The cost is about 290 words, with no measurable change in report length or time.

Limits:

- One model on one harness.
- 1 to 6 samples per cell.
- The not-reproduced branch is unexercised.
- The replay advantage comes from four cases, one of which had a leaked diagnosis.
