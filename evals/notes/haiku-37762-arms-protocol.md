# Haiku 5.5 on react#37762: no skill vs v7 vs v9 (frozen before these runs)

**Status:** exploratory. With 2 runs per arm on one issue, this shows behaviour. It is not proof, and `SKILL.md` does not change on this result. Adopting v9 needs a frozen held-out test on new fix cases.

## The change (v7 → v9)

v9 changes only the fix path. v7's last bullet:

> Leave production code alone until the check fails. If the task is only to reproduce, stop there; otherwise continue from the check.

v9:

> Leave production code alone until the check fails. If the task is only to reproduce, stop there.
>
> When fixing, reproduce every trigger the report names. Name the cause and list the other ways to reach it. For each, add a check, or say why it can't happen or is intended. Don't keep code that no check exercises.

The wording was written after seeing Haiku's v7 run on this same issue (`haiku-37762-observation.md`). Results on this issue are therefore expected to favour v9.

## Runs

- **Model:** Agent tool `haiku`. The served model is checked in each transcript.
- **Arms:** none ×2, v7 ×1 (plus the earlier v7 run), v9 ×2.
- **Batches:** a trio of none, v7 and v9 runs at the same time, then a pair of none and v9.
- **Workspace:** each run gets a clean clone of React `main` (b618bbb4), with no fix branches. `node_modules` is hardlinked from the same install.
- **Prompt:** the same as the first v7 run: the issue text and "Fix this bug.", plus the skill in the v7 and v9 arms. Isolation rules are unchanged, and every transcript is audited.

## Measures

1. **Hidden tests.** Our three regression tests, applied on top of the run's production change:
   - external-store crash;
   - DOM `flushSync` crash;
   - a nested render that suspends without committing, where the update must not be lost.
2. **Behaviour, from the transcript:**
   - (a) a failing reproduction before the first production edit;
   - (b) the triggers reproduced (store, `flushSync`);
   - (c) the suspend-at-the-shell path checked, or explicitly ruled out with a reason;
   - (d) production code that no check exercises;
   - (e) the honesty of the final claims.
3. **Cost:** tokens, tool calls, time.
