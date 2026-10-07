---
name: recreate
description: Turn a bug report into a faithful, runnable reproduction before anything is fixed. Use for bug reports, GitHub issues, regressions, flaky or environment-specific failures, before changing production code.
---

# Recreate

Make the reported failure real before trying to fix it.

## Rules

- Leave production code unchanged until the reported failure is reproduced. Tests, fixtures, scripts, and temporary instrumentation (reverted afterwards) are fine.
- Start with the reporter's exact steps and input on the given revision.
- A reproduction counts only if it shows the *reported* symptom. A related variant you found, a setup error, or a different failure is not the reported bug. Mention it separately if it matters, but don't report it as the reproduction.
- If the reported steps don't fail here, try the reporter's version. If it fails there but not here, it is already fixed: say so instead of looking for variants that still fail.
- If you simulate a condition you can't match (such as another OS), call the result simulated.
- For timing-dependent or flaky failures, repeat until you can state a rate (e.g. `14/100 runs`). One passing run proves nothing.
- If the task is reproduction, stop there. Name the likely cause in one line at most, without tracing it through the code. If the task goes further, reproduce first, then continue.
- Keep context small: read only the code the check needs, run only the relevant test, and trim long output (e.g. `| tail -n 40`).

## The check

Turn the reproduction into one command that a fix can be tested against:

- It exits non-zero while the bug is present and zero once it's fixed. Printing the symptom isn't enough, and no wrapper may hide the exit status.
- It asserts the expected behavior from the report, and nothing else.
- Run it once where the expected behavior holds: a last good version, the report's workaround, or the input without the trigger. Don't write a fix for this. If it still fails, it is checking something else.

## Report

Keep it short. Leave out any section that has nothing in it.

**Status:** Reproduced | Reproduced on <version> only (already fixed) | Reproduced (simulated <condition>) | Not reproduced

Reproduced: **Expected**, **Actual**, **Trigger** (the smallest known condition), **Run** (the check), **Passes when** (where you saw it pass), **Reliability** (if not deterministic), **Artifacts**.

Not reproduced: **Matched**, **Tested**, **Still unknown**, **Need** (the one piece of information that would most reduce uncertainty). Say that no production code was changed.
