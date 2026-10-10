Fixed the "Cannot commit the same tree as before" error (minified #177) for throttled Suspense reveals, and added regression tests.

**Cause.** `completeRoot` flushes the previous commit's pending passive effects before it commits a new tree. Those effects can update the root that is about to commit. Their sync update renders that root inside the flush loop. The render reuses `finishedWork` as its work-in-progress tree and commits it. When `completeRoot` resumes, `finishedWork === root.current`, and the invariant check throws.

**Fix.**
- `packages/react-reconciler/src/ReactFiberWorkLoop.js`: `completeRoot` sets a module flag around its pending-effects flush loop (try/finally). A new exported getter, `isFlushingEffectsBeforeCommit()`, reads it.
- `packages/react-reconciler/src/ReactFiberRootScheduler.js`: `flushSyncWorkAcrossRoots_impl` returns early while the flag is set. Sync work stays scheduled and is flushed by the commit's own flush (`flushSpawnedWork` at commit end) or by the root-schedule microtask, which `ensureRootIsScheduled` always schedules. Every sync render goes through this function, so the guard covers `flushSync`, store-triggered sync updates, and hydration event replay during the loop.
- The invariant check (`finishedWork === root.current` throws) is unchanged. It is now unreachable from the loop.

I did not use the reporter's proposed early return. It only covers a second commit that changes `root.current`. It does not cover a sync render that is left pending without committing, and that render also reuses `finishedWork`.

**Tests.** Two cases were added to `packages/react-reconciler/src/__tests__/ReactSuspense-test.internal.js`. Both use a shared helper that sets up the report's steps: root A throttled by `FALLBACK_THROTTLE_MS`, root B's passive effect still pending.
- Store write through `useSyncExternalStore` in B's passive effect.
- `ReactDOM.flushSync(() => rootA.render(<App />))` in B's passive effect. The test also asserts the expected dev warning that `flushSync` in an effect produces.

**Verification.**
- Before the fix, both new tests fail with "Cannot commit the same tree as before" thrown from `completeRootWhenReady` at the `finishedWork === root.current` check.
- Control: with the trigger removed (the effect no longer writes to the store), the same scenario passes.
- After the fix, both new tests pass, and `ReactSuspense-test.internal.js` passes in full.
- `yarn test packages/react-reconciler`: passes (exit 0).
- Full `yarn test` (default experimental channel): one failure, `ReactFlightAsyncDebugInfo` "does not lose I/O debug info when intermediate promises are garbage collected", which timed out at 5000 ms under full-suite load. The file passes when run alone (20/20). The file is unrelated to this change.
- `yarn flow dom-node`: passes.
- Prettier and ESLint on the three changed files: clean.

**Not covered.**
- Hydration event replay that reaches the same path has no dedicated test. The guard is the same one the tests exercise.
- Suspensey-commit deferrals (completion via a resource callback) are not tested. They share the same `completeRoot` loop, but I did not build a test for that host path.
- The production build was not run. The reporter's observation that 19.0.0 is clean was not reproduced against the published release.
- The `try/finally` exception path is defensive. Nothing exercises it.

Changes are uncommitted in `/work/hk-00c1b10b/repo`: three files modified, 152 insertions and 9 deletions.
