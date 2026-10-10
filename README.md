# Recreate

Turn a bug report into one command that fails while the bug is there, and passes once it's gone.

Recreate is a single agent skill, [`SKILL.md`](SKILL.md) (227 words). It reproduces bugs, and that's all it does: it doesn't fix them. It isn't runtime software: no CLI, MCP server, hooks or telemetry.

## Why

Ask a coding agent to reproduce a bug and it usually finds it. What it hands back often can't be used as a test:
- a script that prints the bug and exits 0;
- a command that fails on both sides, like `tsc`, which exits non-zero by design;
- a check that ends in `; echo`, which swallows the exit code;
- an assertion on what the agent's own fix did, which keeps failing after the real fix.

A check like that can't tell anyone when the bug is gone.

In frozen Sonnet evaluations on real historical issues, every reproduction was replayed against the upstream fix the agent never saw. A reproduction counted only if it failed before that fix and passed after it, showing the reported symptom:

| | No skill | Recreate v5 | Recreate v7 |
|---|---|---|---|
| Reproduction fails before the real fix and passes after it | 4/8 | 22/24 | **16/16** |

Every arm found the bug: the reported symptom showed before the fix in every graded run. The difference is whether the result works as a test. Details are in [`evals/notes/sonnet-v5-results.md`](evals/notes/sonnet-v5-results.md) and [`evals/notes/sonnet-v7-short-results.md`](evals/notes/sonnet-v7-short-results.md).

## Install

Put `SKILL.md` where your agent loads skills, for example `~/.claude/skills/recreate/SKILL.md` for Claude Code, or the matching folder of any agent that supports the Agent Skills format. Agents without skill support can take the text as a system or project instruction, for example in `AGENTS.md`. It uses no vendor-specific tools.

## Use

> Reproduce this issue: <link or text>

> Is this bug still there on main? <link>

> Look into this report before we decide who takes it: <link>

You get back:
- a status (reproduced, already fixed, or not reproduced);
- the command;
- what it showed.

The command is a ready-made check for whoever fixes the bug, and a regression test once they do.

## What it does

- **Reproduces the report, not a cousin of it.** It starts from the reporter's exact steps, and a related failure found on the way is a side note.
- **One command, with an exit code that means something.** Non-zero while the bug is present, zero once it's fixed, asserting only what the report says.
- **Proves the check can pass.** It sees the command pass where the expected behavior holds (a last good version, the report's workaround, or the input without the trigger) without writing a fix.
- **Says "already fixed" when it is.** If the report fails only on the reporter's version, it says so, instead of presenting a nearby variant as a reproduction.
- **States a rate for flaky failures**, and labels simulated environments.
- **Leaves production code alone.** Without a skill, agents asked to "look into" a bug edited production code in 2 of 2 Sonnet runs and 9 of 10 Devin runs. With it: 0 of 2 and 0 of 15.

## Not for fixing

Recreate was tested on "Fix this bug." too, and it didn't help.
- Sonnet without the skill fixed 9 of 10 bugs against upstream's hidden tests; with it, 7 of 10.
- With Haiku, the best run of six had no skill.
- When asked to fix, agents already reproduce first and add a regression test on their own.
- With the skill, their fixes more often stopped at the path their reproduction exercised.

Two attempts to steer the fixing step (v8, v9) didn't change that, so the skill now stops at the reproduction. If you want a fix, ask for it without the skill, and hand the agent the check. The fix evidence is in [`evals/notes/sonnet-fix-results.md`](evals/notes/sonnet-fix-results.md), [`evals/notes/sonnet-fix2-results.md`](evals/notes/sonnet-fix2-results.md) and [`evals/notes/haiku-37762-arms-results.md`](evals/notes/haiku-37762-arms-results.md).

## Versions

- **The current text keeps v7's measured rules word for word.** It replaces v7's last line ("Leave production code alone until the check fails… otherwise continue from the check") with "don't fix it", and narrows the description to reproduction. It hasn't been re-measured on its own. On reproduction tasks v7 already stopped at the check, so it should behave the same.
- **v7** (202 words) replaced v5 (383 words): 16/16 vs 14/16 reproductions, at 13% fewer median tokens. One phrase made the quality difference: "without writing a fix". With a throwaway fix allowed, v5 agents asserted what their own fix did.
- **v5 replaced v3** after adding the one-command check: 5 pairs won, 0 lost, in 24 head-to-head pairs.
- **Earlier v0 to v3** ran as Devin sessions on 18 historical issues. Beyond the production-code result above:
  - Already-fixed reports were stated as already fixed in 5 of 5 runs, against 0 of 6 without the skill.
  - Flaky bugs got a rate in 3 of 3, against 0 of 3.
  - Simulated environments were labelled in 6 of 6.
  - See [`docs/results.md`](docs/results.md).

Older texts are in `evals/variants/` and `evals/notes/`.

## Limits

- The no-skill reproduction arm had one run per case (4/8), against two or more per case for the skill versions.
- Samples are small: 1 to 6 runs per cell, and two harnesses and models (Devin for v0 to v3, Sonnet for v5 and v7).
- The v7 result is near ceiling. It rules out a large loss on these cases, not a small one.
- Simulated environments are labelled, but their fidelity is a known gap. Agents often simulate Windows after the code has already taken the Linux branch (see `evals/notes/audit-2026-10-07.md`).

## Repository

- `SKILL.md`: the skill
- `docs/research.md`: comparable skills, and what Recreate does or doesn't duplicate
- `docs/methodology.md`: cases, arms, isolation, replay grading
- `docs/results.md`: results per case and per instruction
- `cases/`: pinned historical issues and issue snapshots
- `evals/`: prompts, replay grader, raw results and run notes
- `evals/sonnet/`: the Sonnet harness (provisioning, audit, blind review, analysis)
- `handoff/`: the October 2026 GPT-6.1 Sol evidence archive (evaluator-only: it holds upstream fixes)

See [CONTRIBUTING.md](CONTRIBUTING.md) to propose instruction changes.

## License

MIT
