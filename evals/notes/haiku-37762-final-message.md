**Status: reproduced, then fixed.**

**Repro:** `yarn test packages/react-reconciler/src/__tests__/ReactSuspense-test.internal.js -t "interrupted by another root"` (from `/work/haiku-37762/repo`). I added this as a regression test in `ReactSuspense-test.internal.js`. It follows the report's steps: root A has a `Value` that reads a store with `useSyncExternalStore` next to a Suspense boundary with a lazy child; the lazy promise resolves, and the retry commit is throttled with a timer; root B commits `Writer`, whose passive effect calls `store.set(1)`; the timer fires before B's passive effects flush.

- Before the fix: it fails at step 4 with "Cannot commit the same tree as before", thrown from `completeRootWhenReady` through the fake timer. It is deterministic (fake timers and the mock scheduler).
- Same steps with `Writer`'s effect not writing to the store: it passes. So the trigger is the nested synchronous update.

**Cause:** as the report describes. `completeRoot` captures `finishedWork` before the `flushPendingEffects` loop. B's passive effect re-renders A synchronously. That render reuses `root.current.alternate`, which is the same object as `finishedWork`, and commits it. After the loop, `finishedWork === root.current`, so the check throws.

**Fix** (`packages/react-reconciler/src/ReactFiberWorkLoop.js`, `completeRoot`): record `root.current` before the flush loop. After the loop, if `finishedWork` is non-null and either `root.current` changed or a nested render set `root.cancelPendingCommit`, return without committing the stale tree. The lanes stay pending on the root, and the nested commit's `markRootFinished` clears `suspendedLanes`, so the retry renders again. With the fix, the test shows `Value 1` from the synchronous update, then `Lazy` after the retry (throttled again), and a final tree of `Value 1Lazy` and `Writer`.

**Verification:**
- `yarn test packages/react-reconciler`: 77 suites, 1147 tests passed.
- `yarn test packages/react-dom`: 147 of 148 suites passed. `ReactMultiChildText-test.js` hit 30s timeouts under load. It passes when run alone.
- The new test passes under `test-stable` and `test-www`.
- Prettier and eslint are clean on the changed files. `yarn flow dom-node` passes.

**Not covered:**
- The `root.cancelPendingCommit` branch has no test. A noop-renderer attempt (a nested sync render waiting on a suspensey image) committed synchronously and did not reach that branch. The branch follows from the same invariant, but it is unverified.
- A nested sync render that suspends at the shell without committing is not handled. The original code has the same gap. I did not check whether that case is reachable.
