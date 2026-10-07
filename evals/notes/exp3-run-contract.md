# Experiment 3: Run contract (frozen, not run)

The machine-readable plan is `exp3-plan.json`: seed, pair orders, and skill hashes. The protocol was frozen before any outcome existed. Don't edit it after runs start; a change means a new experiment.

## Failure it targets

`SKILL.md` asks for "**Run** (one command)" and never says what the command's exit status means. Faithful reproductions then fail the one property a fixer needs, a check that turns green when the bug is gone:

- eslint-19924, GPT-6.1 Sol (handoff, Exp 2): runs 10304b9c0f82, 41768decd51b and 6fa450bf5532 hit the real `outputFixes` EMFILE but exit 0 while the bug is present and 1 after the fix.
- ripgrep-3009, Devin (`holdout-v0` both arms, `holdout-v3b`): the commands end in `; echo`, so they exit 0 on both sides. The hang shows only in logs.

Those two cases motivated the wording, so they are excluded from evaluation.

## Arms

Only the Report's Run field differs:

| Arm | File | Words | SHA-256 |
|---|---|---|---|
| current | `evals/variants/SKILL-working-291.md` | 291 | `f0bb40aa…f034` |
| candidate | `evals/variants/SKILL-run-contract.md` | 301 | `c3422556…c493` |

Candidate: "**Run** (one command: exit non-zero while the bug is present, zero once fixed)".

Base: the 291-word working copy, because both GPT-6.1 Sol experiments used it. The Run line is identical in v3, so the change ports unchanged.

## Conditions

- **Model:** GPT-6.1 Sol, medium effort, on the same harness as the two earlier experiments. Fresh contexts, no inherited conversation. Don't substitute another model into this experiment.
- **Prompt:** `evals/prompts.py` unchanged, task `reproduce`.
  - The handoff proposed adding the exit convention to the shared prompt. That isn't done here: real users don't state it, and stating it would remove the very behavior under test.
  - Grading handles the confound instead, through `pass_to_fail` and the S endpoint below.
- **Cases:** 4 holdout cases with a hidden upstream fix and existing replay adapters:

  | Case | How the report is naturally reproduced |
  |---|---|
  | pnpm-10290 | CLI output (`pnpm store path`) |
  | ts-60573 | compiler output (`tsc` exit status has its own meaning) |
  | pydantic-11849 | a race script run in trials |
  | eslint-19957 | rule false positive; guards against over-assertion |

  - Cases were chosen from the snapshots: the report is naturally reproduced with a CLI command or script, not a unit test.
  - Disclosure: the controller read Devin-era replay outcomes for these cases during the audit. They were mostly fidelity failures; ts-60573 control r2 is partly an exit-status failure.
  - GPT-6.1 Sol has not run these cases, but they are not untouched holdouts.
- **Scale:** 3 pairs per case, so 12 pairs and 24 contexts.
  - Both orders occur in every case.
  - Each pair runs sequentially, with at most 3 contexts active.
  - Each context gets 600 s, with identical dependencies and build outputs within a pair.
  - No replacements: an interrupted context makes its pair inconclusive.
- **Hygiene:**
  - Directory names visible to agents carry no issue, PR or fix numbers.
  - Upstream patches, this repository and the handoff archive stay outside the agents' filesystem.

## Endpoints

Per run, scored on the replay against the upstream production-only fix (`evals/grade.py`). The adjudicator sees logs and final messages under shuffled ids, then unblinds.

| | Definition |
|---|---|
| **R** (primary) | `fail_to_pass`, and the reported symptom is in the pre log and absent from the post log |
| **S** (guard) | `fail_to_pass` or `pass_to_fail`, with the same symptom check: fix-sensitive in either polarity |
| **A** (guard) | pre shows the symptom, but post still fails on an assertion beyond the report |
| **D** (guard) | production files edited before a faithful reproduction (from telemetry) |
| Effort | seconds to saved artifact, recorded commands, skill words |

## Decision rule

Promote the candidate only if all of the following hold:

1. On R: candidate-only wins minus current-only wins is at least 3, with candidate wins in at least 2 cases.
2. On S: the candidate's total is at least the current arm's total minus 1.
3. On A: the candidate's count is at most the current arm's plus 1.
4. On D: no increase.
5. Time: the per-case median ratio (candidate / current) is at most 1.25 in at least 3 of 4 cases.

Reject if the net R gain is 0 or less. Anything else is inconclusive, and no runs are added to this experiment.

If more than 3 pairs are inconclusive, the whole experiment is inconclusive.

Report the exact two-sided sign test on discordant R pairs. With 12 pairs, 5 wins and 0 losses gives p = 0.0625. The gate is a decision threshold, not a significance claim.

If the current arm never inverts or swallows exit status on these cases, expect rejection. That outcome is informative: it would mean the rule is not needed there.

## If promoted

1. Apply the same one-line change to the root `SKILL.md` (v3 + Run = 299 words) and update the README word count.
2. Record in `docs/results.md` that the change was measured on the 291-word base. Shipping the 291-word copy itself needs its own test (below).

## Queue after this (not frozen)

- **v3 vs the 291-word working copy** on flaky and over-assertion cases (pydantic-11849, urfave-cli-2176, eslint-19957). This decides what the root ships.
- **Environment boundary** (handoff item 3): locate where production reads the missing condition, and model it at that boundary before initialization. Test it on a fresh environment-dependent issue, plus a transfer case where native Linux evidence suffices.
