Fixed the "Cannot commit the same tree as before" error for a throttled Suspense reveal. The changes are in the working tree of /work/hk-22f865f3/repo and are not committed.

Root cause: a deferred commit (the FALLBACK_THROTTLE_MS timer, or a commit waiting on the host) runs completeRoot, which first flushes pending passive effects. If those effects belong to another root and update this one (a store write or a sync update), the flush renders this root synchronously. That render reuses root.current.alternate, which is the finishedWork the deferred commit is about to commit. The stale commit then hits the check finishedWork === root.current and throws. This is the regression from #31930: finishedWork used to live on the root and was cleared by the commit, so the stale call returned early. It is now passed as an argument.

Fix (packages/react-reconciler/src/ReactFiberWorkLoop.js, completeRoot): while passive effects are flushed, completeRoot keeps a cancel callback in root.cancelPendingCommit. prepareFreshStack already calls that callback when a new render of the root starts, so starting such a render marks this commit as superseded. If it was superseded, completeRoot returns without committing; the newer render schedules the remaining work, so the retry still happens. Otherwise the callback is cleared and the commit proceeds as before.

I did not use the check proposed in the report (compare root.current before and after the flush). A passive effect on this root can render it a second time during the same flush, which restores root.current to the earlier tree, so that check misses the stale commit and commits it. The double-commit test below fails under the proposed check and passes with this fix.

Tests (packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js, two new tests after the throttling tests):
- another root's passive effect writes a store read by the throttled root (the report's repro);
- the throttled root is rendered a second time during the flush.
Both fail on the original code and pass with the fix, on the experimental, stable and www-modern channels.

Verification:
- react-reconciler: all 77 suites pass (1148 tests).
- react-dom: one full run had a single timeout failure (ReactMultiChildText, 30s limit under load) that passes on re-run. A parallel run under heavier machine load also timed out in ReactDOMFloat, ReactDOMFizzServer, ReactUpdates, ReactDOMFiber, ReactDOMServerIntegrationElements and ReactDOMTextarea; all of them pass when re-run.
- ReactClassEquivalence reads npm_lifecycle_event, so it has to run via yarn test; it passes that way.
- yarn flow dom-node, prettier and eslint are clean on both changed files.

Notes:
- The flushSync variant from the report does not reproduce in this harness: a flushSync inside a passive effect is deferred until after the timer callback, so no stale commit happens before or after the fix. I have no test for that variant.
- With the fix, any update to the same root during that flush restarts the throttled render, as an update during a suspended commit already does. In that narrow case it costs one extra render.
