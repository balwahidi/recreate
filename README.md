# Recreate

Turn bug reports into reproducible failures.

Recreate is a single agent skill, [`SKILL.md`](SKILL.md) (383 words). It tells a coding agent to make the reported failure real before trying to fix it, and to be honest about what it actually reproduced. It also tells the agent to turn the reproduction into a check that a fix can be tested against. It isn't runtime software: no CLI, MCP server, hooks or telemetry.

## Install

Put `SKILL.md` where your agent loads skills, for example `~/.claude/skills/recreate/SKILL.md` for Claude Code, or the matching skills folder of any agent that supports the Agent Skills format. Agents without skill support can take the text as a system or project instruction (for example in `AGENTS.md`). The instructions don't use vendor-specific tools.

Then:

> Use Recreate on this issue: <link or text>

## What it changes

### Current version (v5), measured with Sonnet

v5 keeps every earlier rule and adds "The check". The reproduction must become one command that:
- exits non-zero while the bug is present and zero once it's fixed;
- asserts only what the report says;
- has been seen passing once, on a last good version or with a throwaway patch that is reverted.

The evaluation had 67 Sonnet runs on 9 real historical issues. Every reproduction was replayed against the real upstream fix, which the agent never saw. Details are in [`evals/notes/sonnet-v5-results.md`](evals/notes/sonnet-v5-results.md).

| | No skill | Previous skill (v3) | Current skill (v5) |
|---|---|---|---|
| Reproduction fails before the real fix and passes after it | 4/8 | 17/24 | **22/24** |
| "Look into this bug" edits production code | 2/2 | 0/2 | 0/2 |
| Already-fixed report stated as already fixed (not a substituted variant) | 0/1 | 2/2 | 2/2 |
| Median tokens per run | 64K | 61K | 64 to 68K |

- **All three arms found the bug every time.** In 56 of 56 graded runs, the reported symptom showed before the fix and was gone after it.
- **The difference is whether the reproduction is usable as a test.** Without "The check", agents often wrote scripts that print the bug and exit 0, ran `tsc` (which fails by design), or ended commands with `; echo`. A fixer can't use those to know when the bug is gone. In 24 head-to-head pairs, v5 won 5, v3 won 0, and 19 tied.
- **No-skill runs edited production code** when only asked to "look into" a bug, and they presented a nearby variant as a reproduction of an already-fixed bug. Both skill versions avoided this.

### Earlier evaluation (v3, Devin sessions)

The earlier findings below come from 18 real historical issues: 7 dev cases and 11 holdout cases. Each compares a control (the same model with no skill) against the skill. Details and caveats are in [`docs/results.md`](docs/results.md).

**Helps:**

- **"Look into this bug" no longer turns into a speculative fix.** Production files were edited in 9 of 10 control runs and 0 of 15 skill runs.
- **"Fix this bug" still fixes, but reproduces first.** On both holdout cases, the control edited production code before running anything. The skill reproduced first and still fixed the bug.
- **Already-fixed reports stay already-fixed.** In one case, the reporter's snippet no longer failed at the checkout. The control reported related variants as "reproduced" in 6 of 6 runs. The skill said "reproduced on 9.37.0 only (already fixed)" in 5 of 5.
- **Flaky bugs get a rate,** such as "9 panics in 100,000 subtests". Control 0 of 3 runs, skill 3 of 3.
- **Simulated environments are labelled.** When the skill simulated Windows on Linux, it put that in the status line in 6 of 6 runs. The control buried it in the body in all 6.
- **Reproductions survive a fix check more often.** In the matched holdout run, the skill passed in 7 of 8 cases and the control in 4 of 8.

**No measurable difference:** finding the bug, reports of behavior that works as designed, and using the project's own test suite. No case triggered the "not reproduced" branch.

### Limits

- Two harnesses and models were used: Devin for v0 to v3, Sonnet subagents for v5. There were 1 to 6 samples per cell.
- The v5 confirmatory round used the two cases where exit status decided pairs. The claim is about that mechanism.
- Simulated-environment fidelity is still a known gap. Agents label Windows simulations correctly, but often simulate after the code has already taken the Linux branch (see `evals/notes/audit-2026-10-07.md`).

## Repository

- `SKILL.md`: the skill
- `docs/research.md`: comparable skills, and what Recreate does or doesn't duplicate
- `docs/methodology.md`: cases, arms, isolation, replay grading
- `docs/results.md`: results per case and per instruction
- `cases/`: pinned historical issues and issue snapshots
- `evals/`: prompts, replay grader, raw results and run notes
- `evals/sonnet/`: the Sonnet harness (provisioning, audit, blind review, analysis)

See [CONTRIBUTING.md](CONTRIBUTING.md) to propose instruction changes.

## License

MIT
