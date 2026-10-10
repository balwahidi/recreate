# Haiku 5.5 with Recreate v7 on react/react#37762 (observation, n=1)

## Setup

- **Model:** `claude-haiku-5-5`, confirmed from the transcript.
- **Workspace:** a clean clone of React `main` at b618bbb4, with none of our fix branches.
- **Skill:** the shipped `SKILL.md` (v7).
- **Report:** the issue text, including the reporter's root cause and proposed fix.
- **Prompt:** "Fix this bug."
- **Isolation:** audited, 0 flags.
- **Cost:** 88 tool calls, 221K tokens, 16 minutes.

## What it did, in order

1. **Read the code.** It read the report, CLAUDE.md, and `completeRoot`, `completeRootWhenReady` and `prepareFreshStack`.
2. **Found the right test home.** It located React's throttling tests, and checked `alwaysThrottleRetries` before relying on the throttle.
3. **Wrote a regression test before touching production code.** It ran the test on the unmodified checkout and got the exact error: "Cannot commit the same tree as before", from the throttle timer. This was step 25.
4. **Ran a control.** The same steps without the store write pass, so the failure depends on the trigger. This is v7's "input without the trigger" pass-check.
5. **Studied the reachable paths.** It checked lane bookkeeping, whether `root.current` can change for other reasons, and how a nested render can leave the root. It grepped `RootSuspendedAtTheShell`.
6. **Made its first production edit at step 41,** after the reproduction and the control. The fix is the reporter's `root.current` check, plus a second condition: bail if a nested render left `root.cancelPendingCommit` set.
7. **Tried to test that second condition.** It deleted the branch and saw its test still pass, then ran the test on the original code. It concluded the test didn't reach the branch. It instrumented `completeRoot` and tried three scenarios (suspensey image, Activity, new Suspense) without reaching it. It then kept the branch and flagged it as untested.
8. **Verified broadly.**
   - Reconciler: 1147 tests passed.
   - react-dom: 147 of 148 suites passed. The other one hit load timeouts, and it reran that file alone, where it passes.
   - The new test passes under stable and www.
   - flow, eslint and prettier are clean.
9. **Reported honestly,** with a "Not covered" section. It named the gap: "A nested sync render that suspends at the shell without committing is not handled... I did not check whether that case is reachable."

## Grading

- **Against our three hidden regression tests:** 2/3.
  - Passes: the store-update crash, and the DOM `flushSync` crash.
  - Fails: a nested render that suspends without committing. That case is reachable, and the update is silently lost: root A ends on "Value: 0" while the store holds 1. This is the gap it named.
- **Its own test:** fails on `main` with the exact error, passes with our fix. A valid reproduction.

## Where Recreate held

- It reproduced before editing production code.
- The check's failure was the reported symptom, and it saw the check pass without the trigger.
- It tested its own extra branch by deleting it, and didn't claim coverage it lacked.
- It reported honestly.

## Where Recreate didn't push it

1. **The narrow fix.** It identified the other path (suspend at the shell) and left it unchecked. It spent its effort on a branch it couldn't reach instead. This is the same failure as Sonnet v7 on vue and ripgrep.
2. **One trigger.** It reproduced the store write, but not `flushSync`, which the report also names.
3. **Untested code.** It kept a branch that no check exercises.
4. **No last good version.** It didn't run the reporter's setup on 19.0.0 and 19.1.0, so it didn't confirm the regression claim.
5. **A partly wrong claim.** "The original code has the same gap" is true of `main`, but 19.0 handled the case.

## Caveat

This is n=1 and has no no-skill Haiku arm. It shows behaviour, not causation.
