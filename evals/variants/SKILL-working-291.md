---
name: recreate
description: Turn a bug report into a faithful, runnable reproduction before anything is fixed. Use for bug reports, GitHub issues, regressions, flaky or environment-specific failures, before changing production code.
---

# Recreate

Make the reported failure real before trying to fix it.

## Rules

- Leave production code unchanged until the reported failure is reproduced. Tests, fixtures, scripts, and temporary instrumentation (reverted afterwards) are fine.
- Start with the reporter's exact steps and input on the given revision.
- Count a reproduction only when it reaches the reported trigger and fails on the reported expected behavior. Extra assertions, related variants, and setup errors are separate findings; keep them from masking the reported symptom.
- If the reported steps don't fail here, try the reporter's version. If it fails there but not here, it is already fixed: say so instead of looking for variants that still fail.
- If you simulate a condition you can't match (such as another OS), call the result simulated.
- For timing-dependent or flaky failures, run a time-bounded batch; report matching failures/completed trials and concurrency settings. Report `0/N` as not reproduced within that budget. One pass proves nothing.
- If the task is reproduction, stop there. A one-line pointer to the likely cause is fine. If the task goes further, reproduce first, then continue.

## Report

Keep it short. Leave out any section that has nothing in it.

**Status:** Reproduced | Reproduced on <version> only (already fixed) | Reproduced (simulated <condition>) | Not reproduced

Reproduced: **Expected**, **Actual**, **Trigger** (the smallest known condition), **Run** (one command), **Reliability** (if not deterministic), **Artifacts**.

Not reproduced: **Matched**, **Tested**, **Still unknown**, **Need** (the one piece of information that would most reduce uncertainty). Say that no production code was changed.
