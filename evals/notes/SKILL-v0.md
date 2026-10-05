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
- Before calling behavior a bug, check it against the project's documented or tested intent. If it behaves as documented, report that.
- Match the conditions that could affect the symptom (version, OS, runtime, config, input) and ignore the rest. If you have to simulate a condition you can't match (such as another OS), call the result simulated.
- Prefer the project's own test or fixture mechanism when it's about as cheap as a standalone script.
- For timing-dependent or flaky failures, repeat until you can state a rate (e.g. `14/100 runs`). One passing run proves nothing.
- If the task is reproduction, stop there. A one-line pointer to the likely cause is fine. If the task goes further, reproduce first, then continue.

## Report

Keep it short. Leave out any section that has nothing in it.

**Status:** Reproduced | Reproduced on <version> only (already fixed) | Reproduced (simulated <condition>) | Behaves as documented | Not reproduced

Reproduced: **Expected**, **Actual**, **Trigger** (the smallest known condition), **Run** (one command), **Reliability** (if not deterministic), **Artifacts**.

Not reproduced: **Matched**, **Tested**, **Still unknown**, **Need** (the one piece of information that would most reduce uncertainty). Say that no production code was changed.
