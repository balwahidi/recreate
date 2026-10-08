Fixed the "Cannot commit the same tree as before" error for the throttled Suspense commit (react/react#37762 scenario).

Cause: completeRoot flushes pending passive effects before committing. A passive effect (store write or flushSync) can synchronously re-render the same root. That render reuses root.current.alternate, which is finishedWork, and commits it. completeRoot then sees finishedWork === root.current and throws.

Change (packages/react-reconciler/src/ReactFiberWorkLoop.js, completeRoot):
- Record root.current before the flush loop.
- After the loop and the "Should not already be working" guard, return early if finishedWork === root.current and root.current changed during the flush. The nested render already committed this tree.
- The original throw guard is unchanged, so a genuine same-tree double commit still throws.

Regression test (packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js, gated on alwaysThrottleRetries): "does not throw when a passive effect re-renders the root of a throttled commit". It fails on the original file with the reported error and passes with the fix.

Verification so far: prettier and eslint pass on both changed files. The full packages/react-reconciler jest run was still in progress when this report was written, so its result is not yet known.

Observations, not fixed:
- If a second synchronous render of the same root happens inside the same flush (a passive effect of the first nested commit writes the store again), the stale commit still goes through. This happens on the original code too; it does not throw. Fixing it needs commit-tracking state beyond this change.
- After the superseded commit, the throttled retry is re-rendered and committed on the next timer advance. The control run (no nested render) shows the same final tree, so this is not caused by the change.
