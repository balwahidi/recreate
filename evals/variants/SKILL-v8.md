---
name: recreate
description: Turn a bug report into a runnable check that fails on the reported bug before anything is fixed. Use for bug reports, GitHub issues, regressions, and flaky or environment-specific failures.
---

# Recreate

Reproduce the reported failure before changing production code.

- Start from the reporter's exact steps and input. Only the reported symptom counts: a related failure you find is a side note, not the reproduction.
- Make it one command that exits non-zero while the bug is present and zero once it's fixed, asserting only what the report says. Before reporting, see it pass where the expected behavior holds (a last good version, the report's workaround, or the input without the trigger), without writing a fix.
- If the report doesn't fail here, try the reporter's version. If it fails only there, say it's already fixed. If it fails nowhere, say so and what you'd need.
- For flaky failures, repeat until you can state a rate. If you simulate an environment, say so.
- Leave production code alone until the check fails. If the task is only to reproduce, stop there. When fixing, fix the cause, not just the path your check exercises: find the other ways to reach that cause and cover them too. A passing check doesn't mean the fix is complete.

Report the status, the command, and what you saw.
