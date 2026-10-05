# Evaluation methodology

## Cases

`cases/cases.json` pins 18 real, closed issues: 7 dev and 11 holdout. The repositories are eslint, vue/core, vite, pnpm, TypeScript, ripgrep, urfave/cli, pydantic and pytest. Each case records:

- the checkout the agent works on (before the fix);
- the upstream fix commit, used only for grading;
- the production files that fix touched.

The case kinds are deterministic bugs, regressions, flaky races, OS-specific reports, already-fixed reports, a report of behavior that is working as designed, and fixture or integration-heavy setups.

`evals/snapshot_issues.py` saves each issue as `cases/<id>/issue.md`. The snapshot stops before the first maintainer diagnosis or linked fix, so the agent sees what a triager would have seen.
The ts-60573 snapshot used in every run had one corrupted snippet (`T['_type',Key]` for `T['_type'][Key]`, from a pagination bug since fixed); both arms saw the same text.

**Known leak.** Four cases were first cut when the fix PR was opened rather than at the first maintainer comment:
- eslint-19245: the root cause;
- eslint-19924: a maintainer's reproduction recipe;
- vite-20705 and ts-60573: the regressing PR.

So in all four, the issue text the agents saw included the maintainers' findings. Every recorded run used those snapshots, in both arms, so the comparison is like-for-like, but those cases were easier than intended. Separately, snapshots used to copy the issue's *current* body. For pydantic-11849, the reporter later edited the body: the edit added a forward-reference field to the example and removed the note that the examples can't reproduce the bug as-is. Every run saw that edited body, which may count as a leak. The snapshots are now cut at the first non-reporter comment, and bodies are taken as they stood at the cutoff, from GitHub's edit history. The versions the runs used are in commit 87769c1. `results.md` reports holdout numbers with and without the leaked cases.

**Holdout use.** The native-test rule was removed after v0, partly on evidence from the v0 holdout run. That makes holdout-v0 the only unseen-data treatment measurement. Later holdout runs (`holdout-v3b`) are reported, but labelled as tuned.

## Arms and prompts

`evals/prompts.py` builds the prompt. Every arm gets the same text: the setup, the issue snapshot, a task line and an output contract. The treatment arm also gets `SKILL.md`, wrapped as an installed skill. The prompt tells the agent not to open the issue page, the fixing PR or commit, or later release notes.

There are three task lines:

| Task | Prompt | What it measures |
|---|---|---|
| reproduce | "Reproduce this bug. Don't fix it; …" | reproduction quality and status honesty |
| investigate | "Look into this bug report." | speculative production edits |
| fix | "Fix this bug." | that the skill doesn't block a requested fix |

The evaluated agent returns `final_message`, `patch` (its whole working tree diff) and `run_command`.

## Harness

`evals/workflow.py` runs each (case, arm, task, repeat) as an independent Devin session, all on the same model. That means a single harness and a single model: the results don't show how other agents behave.

**Isolation.** Evaluated sessions are told not to read or write persistent memory. Without that line, sessions in an early batch saved case notes to shared memory, and later runs read them. Those runs (`holdout-v3`, `ablation-v2`, `treatment-v1-probe`) are excluded. The clean reruns are `holdout-v3b` and `ablation-v2b`.

## Replay grading

`evals/grade.py <run> [label filters]` grades a run by replaying it:

1. Reset to the checkout and apply the agent's patch.
2. Run `run_command`: the "pre" side.
3. Apply only the upstream production fix.
4. Run the command again: the "post" side.

A useful reproduction is `fail_to_pass`: non-zero exit before the fix, zero after. Commands for flaky cases run 3 times per side. Every verdict comes with pre and post logs, and I read the logs before accepting a verdict.

Per-case adjustments, all in `grade.py` or the grading environment:

- **vite, TypeScript:** rebuild generated output after each patch (`BUILD`).
- **urfave/cli:** the fix changes an API the reproduction uses, so the upstream test patch is applied with the fix (`POST_EXTRA`).
- **ripgrep:** the fix adds a test with the same name as the reporter's, so grading uses the production hunks only (`fix_grade.patch`). Agents' wrapper commands exit 0 even on a hang, so the verdict comes from the logged output: a hang before the fix and a return after it.
- **TypeScript:** the checkout uses CRLF line endings. Grading uses the production-only fix diff and checks that one file out with LF.
- Cases with no upstream fix (already fixed, OS-specific, working as designed) are graded by reading the report.

## Metrics

- **Faithful reproduction:** `fail_to_pass`, and the observed symptom matches the report.
- **False or substituted reproduction:** claiming "reproduced" with a nearby variant, a simulated environment presented as native, or behavior that is intended.
- **Speculative production edits:** production files in the patch on `investigate`, and production edits made before any reproduction ran (read from session timelines).
- Report length in words, and session minutes compared within the same run.

**Grader isolation.** Each side starts from a reset checkout, with the agent patch reapplied. Git-ignored files (installed dependencies, build caches) are kept between sides and samples, because reinstalling for every side is too costly. Generated output that the commands consume is rebuilt on each side (`BUILD`). Other ignored state could still carry over, which is one more reason the logs behind each verdict that separates the arms were read by hand.
