Status: reproduced, then fixed. The check fails before the fix and passes after it.

Check (recreate step): a regression test was added to packages/react-reconciler/src/__tests__/ReactSuspense-test.internal.js, titled "does not throw when another root's passive effects update a throttled retry". It runs the report's steps with react-dom and jest fake timers, using the repo's Scheduler mock and React.lazy.

Command: yarn test packages/react-reconciler/src/__tests__/ReactSuspense-test.internal.js -t "another root"

Before the fix, it fails at step 4 with "Cannot commit the same tree as before. This error is likely caused by a bug in React." The error is thrown from completeRootWhenReady through completeRoot when the throttle timer fires.

Control (no trigger): the same steps with the store write removed, run on the unfixed code, do not throw at step 4.

flushSync variant (flushSync(() => rootA.render(<App />)) in the passive effect): throws the same error on the unfixed code and does not throw with the fix. In dev it logs the expected "flushSync was called from inside a lifecycle method" warning. I did not keep this variant in the repo.

After the fix, the test passes. Step 4 does not throw, and the final tree is "value:1A" with store value 1.

Root cause (confirmed): the throttle timer clears root.timeoutHandle, then completeRoot runs its flushPendingEffects loop. That flush runs root B's passive effect, store.set(1) schedules a sync update on root A, and the sync render reuses root.current.alternate, which is the same fiber object as the deferred finishedWork. The sync render commits it. completeRoot then sees finishedWork === root.current and throws. Nothing cancels the deferred commit, because the timer has already fired.

Fix (packages/react-reconciler/src/ReactFiberWorkLoop.js, completeRoot): record root.current before the flush loop. After the loop, if finishedWork === root.current and root.current changed during the flush, return instead of committing. The existing throw is kept for the case where finishedWork was already current before the flush. This is the reporter's proposed fix. It only changes the case that previously threw.

Why the retry is not lost: the nested sync commit calls markRootFinished, which clears suspendedLanes and recomputes pendingLanes from the fibers. The retry lane stays on the Suspense fibers. In the test the retry re-renders (logs "Child"), is throttled once more because the fallback was shown recently, and commits after the throttle with the correct final tree.

Other checks:
- yarn test packages/react-reconciler: 77 suites passed, 1147 tests passed.
- yarn test packages/react-dom: 146 suites passed. Two suites failed on 5s and 30s timeouts under load (ReactDOMServerIntegrationAttributes-test.js, ReactMultiChildText-test.js). Run alone with the fix, both pass (554 tests). I did not run them on the unfixed tree.
- yarn test-stable and yarn test-www on packages/react-reconciler/src/__tests__/ReactSuspense*: 221 tests passed on each channel.
- prettier --check and eslint: clean on both changed files.
- yarn flow dom-node: no errors.

Not done: I did not write a test for the non-throttled path. The fix is in completeRoot, so it also applies there, but I did not verify that path. I also did not compare against 19.0.0 as the report's last-good version. The no-trigger control covers the "input without the trigger" check instead.

Changed files (working tree only, nothing committed or pushed):
- /work/hk-9f803ca8/repo/packages/react-reconciler/src/ReactFiberWorkLoop.js
- /work/hk-9f803ca8/repo/packages/react-reconciler/src/__tests__/ReactSuspense-test.internal.js
