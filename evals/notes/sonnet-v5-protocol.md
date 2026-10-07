# Sonnet evaluation of the v5 redesign (frozen before any run)

## Question

Does v5 (`evals/variants/SKILL-v5.md`, 383 words, SHA-256 `06a8a675…7619`) produce more reproductions that fail before the real upstream fix and pass after it than the shipped v3 (`SKILL.md`, 289 words, `3e89ff91…f5aa`)? It must do that without losing discipline, honesty or too much efficiency.

If v5 doesn't clear the rule below, v3 stays.

## What v5 changes

v5 keeps every v3 rule word for word. It adds a "The check" section and a **Passes when** report field. The run command must:
- exit non-zero while the bug is present and zero once fixed;
- assert only the reported expected behavior;
- be seen passing once where the expected behavior holds (a last good version, or a throwaway patch that is then reverted).

Each part targets an observed failure:

| Failure | Where it was seen |
|---|---|
| Inverted exit status | eslint-19924, GPT-6.1 Sol |
| Swallowed exit status | ripgrep-3009, Devin |
| Exit status meaningless by design (`tsc`) | ts-60573 |
| Assertions beyond the report | eslint-19957 |
| Unrelated errors counted | pydantic-11849 |
| Missing baseline files | ts-60573 |

## Setup

- **Evaluated agents:** Sonnet, as Agent-tool subagents in fresh contexts.
- **Prompt:** `evals/sonnet/harness.py`. It is the repository prompt adapted to a pre-provisioned checkout.
- **Workspace:** each agent works in `/work/runs/<random id>`, with dependencies installed. Its checkout never contains the fix commit.
- **Pairing:** the two arms of a pair run at the same time, so they share load.
- **Isolation is instructed, not enforced** (same user, same machine). Transcripts are audited afterwards for reads outside the workspace and for lookups of the resolution; an offending run is excluded and reported.
- **Patches:** computed by the controller with `git add -A && git diff <checkout>`.

## Runs (`plan-main`)

| Case | Task | Pairs | Graded by |
|---|---|---|---|
| eslint-19957, eslint-19924, eslint-19637, vue-13611, urfave-cli-2176, pydantic-11849, ripgrep-3009, ts-60573 | reproduce | 2 each | replay against the upstream production fix |
| eslint-20209-fixed (already fixed) | reproduce | 2 | reading the status |
| eslint-19637, vue-13611 | investigate | 1 each | production files in the final patch |

That's 40 runs in total.

After the main runs, a no-skill context arm (`plan-context`, 1 run per unit) measures the skill's absolute effect. It doesn't enter the decision.

## Endpoints

| Endpoint | Definition |
|---|---|
| **R** (primary) | replay verdict `fail_to_pass`, and blind log review finds the reported symptom on the pre side and not on the post side |
| **S** | `fail_to_pass` or `pass_to_fail`, with the same symptom check (fix-sensitive in either polarity) |
| **P** | production files in the final patch on reproduce and investigate runs |
| **H** | eslint-20209-fixed: the status says already fixed, and no variant is presented as the reproduction |
| **Cost** | total tokens, tool uses and duration per run, from the Agent tool's usage report |

Blind review means logs are read under random run ids, with arms looked up only after every verdict is written.

## Decision rule

Over the 16 graded reproduce pairs, the net R gain is v5-only passes minus v3-only passes.

Adopt v5 only if all of the following hold:
1. The net R gain is at least 3.
2. v5's S total is at least v3's S total minus 1.
3. v5's P total is no higher than v3's.
4. v5's H count is at least v3's.
5. v5's median total tokens are at most 1.5 times v3's.

Outcomes:
- Net R gain of 0 or less: reject.
- Net R gain of 1 or 2: inconclusive. v3 stays, and the result is reported.
- Agent errors or excluded runs: the pair is dropped. If more than 4 pairs drop, the experiment is inconclusive.

Known limits: one model, 2 samples per case, and cases whose failure modes motivated v5 (eslint-19957, eslint-19924, ts-60573, pydantic-11849, ripgrep-3009). eslint-19637, vue-13611 and urfave-cli-2176 did not motivate it. Results are reported for both groups.
