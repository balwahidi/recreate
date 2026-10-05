# Recreate

Turn bug reports into reproducible failures.

Recreate is a single agent skill, [`SKILL.md`](SKILL.md) (289 words). It tells a coding agent to make the reported failure real before trying to fix it, and to be honest about what it actually reproduced. It isn't runtime software: no CLI, MCP server, hooks or telemetry.

## Install

Put `SKILL.md` where your agent loads skills, for example `~/.claude/skills/recreate/SKILL.md` for Claude Code, or the matching skills folder of any agent that supports the Agent Skills format. Agents without skill support can take the text as a system or project instruction (for example in `AGENTS.md`). The instructions don't use vendor-specific tools.

Then:

> Use Recreate on this issue: <link or text>

## What it changes

Each finding below compares a control (the same model with no skill) against the skill, on 18 real historical issues: 7 dev cases and 11 holdout cases. Details and caveats are in [`docs/results.md`](docs/results.md).

**Helps:**

- **"Look into this bug" no longer turns into a speculative fix.** Production files were edited in 9 of 10 control runs and 0 of 15 skill runs.
- **"Fix this bug" still fixes, but reproduces first.** On both holdout cases the control edited production code before running anything. The skill reproduced first and still fixed the bug.
- **Already-fixed reports stay already-fixed.** In one case the reporter's snippet no longer failed at the checkout. The control reported related variants as "reproduced" in 6 of 6 runs; the skill said "reproduced on 9.37.0 only (already fixed)" in 5 of 5. On a second already-fixed case both arms did well.
- **Flaky bugs get a rate,** such as "9 panics in 100,000 subtests". Control 0 of 3 runs, skill 3 of 3.
- **Simulated environments are labelled.** When the skill simulated Windows on Linux, it put that in the status line in 6 of 6 runs. The control buried it in the body in all 6.

- **Reproductions survive a fix check more often.** On holdout cases, a reproduction counts when it fails before the real upstream fix and passes after it. In the matched holdout run (one sample per case and arm), the frozen skill passed in 7 of 8 cases and the control in 4 of 8. Without two cases whose issue text leaked the maintainers' diagnosis, that's 5 of 6 vs 3 of 6. Extra control samples on the cases where the arms differed passed 3 of 8 times. The control always found the bug, but its tests sometimes:
  - asserted more than the report said;
  - exercised a different code path from the command the reporter ran;
  - counted unrelated errors as the bug.

**No measurable difference:**

- **Finding the bug.** Both arms showed the reported symptom on every holdout case. Dev-case reproductions passed the fix check in both arms (8 of 8 each).
- **Reports of behavior that is working as designed.** One report described a rule doing what its docs say. Both arms called it a bug, even with an explicit rule (0 of 4 skill runs). That rule was removed.
- **Using the project's own test suite.** Results were mixed, so that rule was removed too.
- **"Not reproduced" reports.** No case triggered one, so this part of the skill is untested.

**Cost:** about 290 words of instructions. Report length and session time were about the same in both arms.

The honest summary: modern agents already find and reproduce reported bugs well. Recreate helps in three ways:

- it stops production edits before a reproduction exists;
- it keeps the status honest (already fixed, simulated, flaky rate);
- it makes the reproduction a tighter check of the reported behavior.

Limits: everything was run on one harness and one model, as Devin sessions, with 1 to 6 samples per cell. Other agents may behave differently.

## Repository

- `SKILL.md` — the skill
- `docs/research.md` — comparable skills and what Recreate does or doesn't duplicate
- `docs/methodology.md` — cases, arms, isolation, replay grading
- `docs/results.md` — results per case and per instruction
- `cases/` — pinned historical issues and issue snapshots
- `evals/` — prompts, workflow runner, replay grader, raw results and run notes

See [CONTRIBUTING.md](CONTRIBUTING.md) to propose instruction changes.

## License

MIT
