---
name: recreate
description: Reproduce a bug report as one command that fails while the bug is present and passes once it's fixed, then stop. Use when asked to reproduce, triage or look into a bug report, GitHub issue, regression, or flaky or environment-specific failure, or to check whether a reported bug still happens. It doesn't fix bugs.
---

# Recreate

Make the reported failure real, and hand back a check anyone can run. Don't fix it.

- Start from the reporter's exact steps and input. Only the reported symptom counts: a related failure you find is a side note, not the reproduction.
- Make it one command that exits non-zero while the bug is present and zero once it's fixed, asserting only what the report says. Before reporting, see it pass where the expected behavior holds (a last good version, the report's workaround, or the input without the trigger), without writing a fix.
- If the report doesn't fail here, try the reporter's version. If it fails only there, say it's already fixed. If it fails nowhere, say so and what you'd need.
- For flaky failures, repeat until you can state a rate. If you simulate an environment, say so.
- Don't change production code, even when the fix looks obvious. The check is the deliverable.

Report the status, the command, and what you saw.
