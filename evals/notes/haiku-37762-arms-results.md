# Haiku 5.5 on react#37762: results (no skill vs v7 vs v9)

Protocol: `haiku-37762-arms-protocol.md`, frozen before these runs. This is exploratory: 2 runs per arm on one issue. **`SKILL.md` does not change.**

## Result

Neither skill improved the outcome. The only run to pass all three hidden tests used no skill.

v9 did change what Haiku tested, as intended: both v9 runs reproduced both triggers the report names. That did not carry over to the deeper failure path.

| Run | Arm | Hidden tests | Store | `flushSync` | Suspends without committing | Tokens | Tool calls | Time |
|---|---|---|---|---|---|---|---|---|
| 22f865f3 | none | **3/3** | pass | pass | pass | 342K | 180 | 30 min |
| 8bd9a9c7 | none | 2/3 | pass | pass | fail | 250K | 89 | 14 min |
| (earlier) | v7 | 2/3 | pass | pass | fail | 221K | 88 | 16 min |
| 9f803ca8 | v7 | 2/3 | pass | pass | fail | 165K | 57 | 19 min |
| 29cea7ca | v9 | 2/3 | pass | pass | fail | 206K | 79 | 28 min |
| 00c1b10b | v9 | 1/3 | fail | pass | fail | 223K | 73 | 18 min |

Every run was served by `claude-haiku-5-5`. The audit found no isolation breaks: no file reads outside each run's workspace, no web access, and no lookup of the issue's fix.

## Behaviour (from the transcripts)

**(a) Failing reproduction before the first production edit:** all five runs. This held without the skill too.

**(b) Triggers reproduced:** this is where v9 changed behaviour.
- Both v9 runs kept a test for the store trigger and one for the `flushSync` trigger.
- Both no-skill runs and the v7 run kept a store test only.
  - 22f865f3 tried `flushSync` and reported that it does not reproduce in its harness.
  - 9f803ca8 ran a `flushSync` variant but did not keep it.

**(c) The deeper path:** the stale tree committed without a throw, either through a second nested render or one that suspends.
- 22f865f3 (none) found it, rejected the reporter's proposed fix with a failing test, and fixed it through `cancelPendingCommit`. This is the same design as our fix.
- 8bd9a9c7 (none) found the double-render case and left it unfixed, saying so.
- 29cea7ca (v9) saw the lost retry ("the lazy child never appears") and called it a separate, pre-existing bug.
- 9f803ca8 (v7) argued that the retry is not lost. That holds for its own test, not for the hidden case.

**(d) Code no check exercises:**
- 00c1b10b (v9) kept a `try/finally` path and a hydration-replay guard without checks. It disclosed both, despite the v9 line "Don't keep code that no check exercises."
- The other runs kept only code their tests exercise.

**(e) Honesty:** no fabricated results.
- 8bd9a9c7's final message says its full suite was still running. It corrected this in its hand-back.
- 9f803ca8's "the retry is not lost" claim is broader than its evidence.

## Why v9's second run scored 1/3

Its fix is a different design. It stops sync work from flushing while `completeRoot` flushes passive effects, so the nested render waits and the throttled tree commits first.

Hidden tests 1 and 3 assert React's existing rule: when a new render of the root starts, `prepareFreshStack` cancels any pending commit. The throttled tree must therefore not commit. This run's final store value is current, but the superseded tree commits, and `flushSync` inside that flush no longer flushes synchronously.

Its v9-driven step, listing other ways to the cause (hydration replay, other sync paths), led it to a wider scheduler change instead of fixing the commit.

This means the hidden tests partly grade design, not only the crash. Against React's own invariant, the design is still the weaker one.

## What this says about Recreate

- On a hard fix in a reconciler, the skill did not make Haiku's fixes more correct. The run-to-run spread without the skill (3/3 vs 2/3) is as large as any difference between arms.
- v9's trigger rule works as a behaviour change: both runs covered both triggers. But the decisive bug was a path no trigger names, and only one run, without the skill, found it.
- The "list other ways to reach it" line can push toward wider fixes. Here that cost a correct design.
- Skill runs were cheaper here: a median of 206K tokens with a skill vs 296K without. With n=2, that is noise until shown otherwise.

**Decision:** keep v7 as shipped, as the protocol required.

Before adopting any fix-path wording, it has to pass a frozen held-out test on new fix cases, comparing:
- v7 alone vs v7 plus "reproduce every trigger the report names";
- the trigger line without "list the other ways".

Files: each run's production diff and final message are in `haiku-37762-arms/`.
