# Sonnet evaluation of v5: results

Protocols (frozen before their runs):
- `sonnet-v5-protocol.md` (main run)
- `sonnet-v5-confirm-protocol.md` (confirmatory round)
- `sonnet-symptoms.md` (symptom criteria)

Plans with seeds and run ids are in `sonnet-plan-*.json`. Raw results and replay logs are in `evals/results/sonnet-{main,confirm,context}/`, blind verdicts in `sonnet-adjudication.json`, and analysis output in `sonnet-*-analysis.txt`.

**Decision: v5 replaces v3 as `SKILL.md`.** The main run was inconclusive under its rule (net +2). The confirmatory round cleared its rule: net +3, no losses, S and cost guards met.

## Primary metric

R is a reproduction that fails before the real upstream fix and passes after it, showing the reported symptom.

| Case | Main: v3 | Main: v5 | Confirm: v3 | Confirm: v5 | No skill |
|---|---|---|---|---|---|
| eslint-19957 | 2/2 | 2/2 | | | 1/1 |
| eslint-19924 | 1/2 | 2/2 | 2/4 | 4/4 | 0/1 |
| eslint-19637 | 2/2 | 2/2 | | | 1/1 |
| vue-13611 | 2/2 | 2/2 | | | 1/1 |
| urfave-cli-2176 | 2/2 | 2/2 | | | 1/1 |
| pydantic-11849 | 2/2 | 2/2 | | | 0/1 |
| ripgrep-3009 | 0/2 | 0/2 | | | 0/1 |
| ts-60573 | 1/2 | 2/2 | 3/4 | 4/4 | 0/1 |
| **Total** | **12/16** | **14/16** | **5/8** | **8/8** | **4/8** |

Across both v3-vs-v5 rounds, 24 pairs: v5 won 5, v3 won 0, and 19 tied. The exact two-sided sign test on the 5 discordant pairs gives p = 0.0625.

**Every graded run in every arm reproduced the reported symptom.** The symptom was in the pre log and gone from the post log in 56 of 56 graded runs. So R equals the mechanical `fail_to_pass` verdict for every run, and no decision rests on a judgment call.

## Every miss, and why

| Arm | Run | Case | Why it misses |
|---|---|---|---|
| v3 | 67029e898f, 866f289585, d3c635b434 | eslint-19924 | the script prints eslint's exit code but exits 0 itself |
| v3 | 2a02f47ca2 | ts-60573 | the check runs `tsc`, which exits 2 by design on both sides |
| v3 | c7abe918d8 | ts-60573 | a print-only script that exits 0 on both sides |
| v3 | c154c8876a, 629867e318 | ripgrep-3009 | `; echo` swallows the hang's exit status |
| v5 | ce7ae07610, 1e967925f2 | ripgrep-3009 | the hang fails correctly (124), but the reporter's own `should_panic(expected = "oops!")` fails after the real fix, which re-panics with a different message |
| none | 278e86b1ef | eslint-19924 | exits 0 on both sides |
| none | c23ecc3639 | ts-60573 | exits 0 on both sides |
| none | c68e820f51 | ripgrep-3009 | `; echo` |
| none | 90e235621a | pydantic-11849 | the script's own instrumentation, tied to rebuild internals, times out after the fix |

Every v3 miss is an exit-status failure, which is what v5's "The check" section targets. v5's only misses are on the ripgrep ceiling, which every arm and every earlier evaluation hit.

## Guards

| | v3 | v5 | No skill |
|---|---|---|---|
| **H:** already-fixed report (eslint-20209-fixed) stated as already fixed, with no variant substituted | 2/2 | 2/2 | 0/1 ("could not reproduce the exact example, but reproduced the same bug with close variants") |
| **P:** production files in the final patch on "Look into this bug report." | 0/2 | 0/2 | 2/2 |
| **P:** same, on reproduce | 0/26 | 0/26 | 0/9 |
| **A:** over-assertion | 0 | 0 | 0 |

The ripgrep patches touch `walk.rs` only inside its `mod tests` block (the reporter's test), so they don't count as production edits.

## Cost

Medians per run, from the Agent tool's usage report:

| | Main: v3 | Main: v5 | Confirm: v3 | Confirm: v5 | No skill |
|---|---|---|---|---|---|
| Tokens | 61.5K | 68.2K | 61.0K | 64.5K | 64.0K |
| Tool calls | 16 | 16.5 | 14.5 | 17 | 13 |
| Seconds | 157 | 184 | 248 | 238 | 153 |

v5 costs about 6 to 11% more tokens, well under the 1.5× ceiling. Its text grows from 289 to 383 words. Times are noisy, because up to 11 agents shared 4 CPUs.

## What v5 agents did differently

Reading the final messages (arms visible), v5 agents made their check pass once before reporting. Their **Passes when** field recorded:
- running the check on the last good release (eslint 9.24.0, TypeScript 5.6.3);
- running it with the report's workaround (ts-60573);
- running it with a throwaway patch, then reverting it (eslint-19957, eslint-19924, urfave-cli-2176, ripgrep-3009).

No throwaway patch was left in a final tree: P stayed at 0.

## Audit, isolation and blinding

- **Transcripts:** all 67 runs (40 main, 16 confirm, 11 context) were scanned for tool calls outside the agent's workspace, the grading checkouts, other runs, the controller's files, and lookups of the issue, PR or fix commit. 66 were clean. One fetched the reporter's linked core-js ESLint config pinned to the report date, which is allowed reference material.
- **Isolation** was instructed, not enforced: same machine and user. A first attempt at a separate unprivileged agent user was blocked by the environment's safety check, so the Agent tool was used instead.
- **Blinding was partial.**
  - The controller launched runs knowing their arms.
  - 7 agents returned their full report instead of `DONE`, which revealed the arm.
  - Symptom review used logs under random ids.
  - Because every run showed the symptom, the verdicts are mechanical and the blinding gaps can't have moved a decision.
- **Pilot:** the pilot pairs (eslint-19637 investigate, ripgrep-3009) are counted. The harness wasn't changed in any way that affects agents. Only the audit's false positives were fixed.

## Limits

- One model: Sonnet, as Agent-tool subagents. The earlier GPT-6.1 Sol experiments ran a different skill copy, so results are not pooled.
- 2 to 4 samples per case. The confirmatory cases were chosen because exit semantics decided pairs in the main run. The claim is about that mechanism, not about every case type.
- Five main-run cases motivated v5's wording: eslint-19957, eslint-19924, ts-60573, pydantic-11849 and ripgrep-3009. eslint-19637, vue-13611 and urfave-cli-2176 did not, and v5 tied v3 on them.
- v5 doesn't find more bugs; every arm found the symptom every time. It makes the artifact usable as a regression check: it fails now and passes once the bug is fixed.
- Not exercised here: environment simulation fidelity (the pnpm-16217 gap) and the "not reproduced" branch.
