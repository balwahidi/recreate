# ignore: parallel walker occasionally hangs if visitor panics

Reported by @cosmicexplorer on 2025-03-06

### Please tick this box to confirm you have reviewed the above.

- [x] I have a different issue.

### What version of ripgrep are you using?

master (de4baa10024f2cb62d438596274b9b710e01c59b)

### How did you install ripgrep?

I am able to reproduce this on `master`.

### What operating system are you using ripgrep on?

Arch Linux (64-bit, x86):

```shell
> uname -a
Linux terrestrial-gamma-ray-flash 6.13.5-zen1-1-zen #1 ZEN SMP PREEMPT_DYNAMIC Thu, 27 Feb 2025 18:09:27 +0000 x86_64 GNU/Linux
```

### Describe your bug.

`WalkParallel::visit()` will nondeterministically hang if the `ParallelVisitor::visit()` implementation panics. This also occurs when providing a closure to `WalkParallel::run()`.

### What are the steps to reproduce the behavior?

I am working on a minimal fix to this right now (see https://github.com/BurntSushi/ripgrep/compare/master...cosmicexplorer:ripgrep:parallel-panic-quit?expand=1), but I think it will require a change to the parallelization methods we use from crossbeam, so I wanted to create this issue beforehand. I am currently able to reproduce this with the following:

```diff
diff --git a/crates/ignore/src/walk.rs b/crates/ignore/src/walk.rs
index d6ea9c2..4387fca 100644
--- a/crates/ignore/src/walk.rs
+++ b/crates/ignore/src/walk.rs
@@ -2221,6 +2221,18 @@ mod tests {
         assert!(!dents[0].path_is_symlink());
     }
 
+    #[test]
+    #[should_panic(expected = "oops!")]
+    fn panic_in_parallel() {
+        let td = tmpdir();
+        wfile(td.path().join("foo.txt"), "");
+
+        WalkBuilder::new(td.path())
+            .threads(40)
+            .build_parallel()
+            .run(|| Box::new(|_| panic!("oops!")));
+    }
+
     #[cfg(unix)] // because symlinks on windows are weird
     #[test]
     fn symlink_loop() {

```

Apply the above diff, then run the following command:

```shell
> cd crates/ignore
> timeout -k 2 1 cargo test --lib -- parallel
```

I typically have to run this many many times on my very fast laptop to get it to trigger. More reliably, you can run:

```shell
> cd crates/ignore
> cargo test
```

And running all the tests at once makes this trigger much more reliably.

### What is the actual behavior?

The process hangs, typically somewhere in the `Worker::get_work()` method. If I add a print statement within this sub-`loop`: https://github.com/BurntSushi/ripgrep/blob/de4baa10024f2cb62d438596274b9b710e01c59b/crates/ignore/src/walk.rs#L1695-L1707 it will print this out endlessly.

This especially seems to occur more often if the panic handler is non-trivial: I first noticed this when using `color-eyre`, which prints the panic to the console after composing a backtrace.

### What is the expected behavior?

The `WalkParallel::visit()` method should not hang, and should instead propagate the panic.

My first attempt to solve this (see https://github.com/cosmicexplorer/ripgrep/commit/246c1621760b41f631606c7b3061a25efe86e0fc) set the `quit_now` flag if any worker panics, and checked `self.is_quit_now()` within the sub-`loop`. This seems to have made it repro less often, but I am still able to get it to repro regardless, even without modifying the panic handler.

There are some other changes I want to propose to the `ParallelVisitor{,Builder}` traits as well which may make this easier (such as propagating unwind safety), but I'm currently hoping to solve this without making any changes to the external interface. This may require changing the parallelism primitives we use, but maybe not.
