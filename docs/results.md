# Results

All runs use one harness and one model: Devin sessions, with identical prompts in both arms (see `methodology.md`). Raw outputs and replay logs are in `evals/results/<run>/`, and decisions are recorded in `evals/notes/baseline-dev-v1.md`. The shipped skill is v3, the 289-word `SKILL.md`.

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
