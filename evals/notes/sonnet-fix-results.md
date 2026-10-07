# Fix test: v7 vs no skill on "Fix this bug.": results

Protocol: `sonnet-fix-protocol.md`, frozen before any run, with a grader-only amendment made before any run was graded. Plan: `sonnet-plan-fix.json`. Raw results: `evals/results/sonnet-fix/`. Analysis: `sonnet-fix-analysis.txt`. Claims: `sonnet-fix-claims.json` (blind). Audit: `sonnet-fix-audit.txt`.

**Under the frozen rule: "Recreate fixes worse."** No-skill fixed correctly in 2 pairs where v7 didn't. v7 won none, and 8 pairs tied. With 10 pairs this is weak evidence, but it clearly isn't the improvement the test was looking for. `SKILL.md` is unchanged, as the protocol said in advance.

## Results

| | No skill | v7 |
|---|---|---|
| F: passes upstream's hidden tests and the existing neighbours | **9/10** | 7/10 |
| Pairs won | 2 | 0 (8 ties) |
| Final message claims a fix with a before/after check (blind) | 9/10 | 10/10 |
| Patch adds a regression test | 10/10 | 10/10 |
| Overclaims: claimed fixed, failed hidden tests | 1 | 3 |
| Median tokens | 80.6K | 86.4K (cheaper in 4 of 10 pairs) |
| Median tool calls / time | 21.5 / 8.3 min | 29.5 / 12.6 min |

Per case (no skill / v7):
- eslint-19957: 2/2, 2/2.
- eslint-19924: 2/2, 2/2.
- ts-60573: 2/2, 2/2.
- ripgrep-3009: 2/2, 1/2.
- vue-13611: 1/2, 0/2.

## What the misses have in common

Every miss fixed the path the reproduction exercised and stopped there. Upstream fixed the shared cause.

- **vue-13611** (both v7 runs, 1 no-skill run): the fix stops skipping `_`-prefixed keys when compiled slots are assigned. Slots passed through a render function still drop `_foo`, and upstream's test checks that path.
  - The narrow runs kept an existing test expecting those keys to be ignored; upstream changed that test. The narrow fix is defensible, but it isn't what upstream shipped.
- **ripgrep-3009** (1 v7 run): the fix handles a panic in the visitor, which is the report's scenario. The walk still hangs when the panic is in the visitor builder, which upstream's second test covers.

Narrow fixes: no skill 1/10, v7 3/10.

A plausible mechanism, not tested here: v7 tells the agent that only the reported symptom counts, then to "continue from the check". An agent that defines done as "my check passes" has no prompt to look beyond the reported path.

## What the no-skill arm already does

The fix-task prompt didn't ask for a reproduction. Even so, 9 of 10 no-skill agents said they saw a check fail before the change and pass after it, and all 10 added a regression test.

On fix tasks, Sonnet already does what Recreate asks for. The two improvements considered earlier, "keep the check as the regression test" and "the fix is done when the check passes", would add nothing it doesn't already do. The second may even be the problem.

## Integrity

- **Graders.** Each was checked before any run: it fails at the checkout and passes twice with the upstream fix. Changes after launch, all made before any run was graded unless noted:
  1. agents' own tests are excluded;
  2. each grading command gets a private `TMPDIR`, because ESLint fixtures in `/tmp` are shared with running agents;
  3. mocha gets a 60 s timeout, because tests timed out under load;
  4. patch sections for files the grader overwrites anyway are skipped, so they can't block applying the patch.

  After all runs, the 20 runs were regraded with the final grader, and no verdict changed.
- **Line endings.** One TypeScript run (ceb2fe0a4a, v7) was collected before a collector bug was fixed: Python's text mode had turned CRLF into LF in its patch. CRLF was restored on `checker.ts`, which is all-CRLF at the checkout, and the run passes. Later runs are collected as bytes.
- **Audit.** No run fetched anything from GitHub or the web.
  - 13 of 20 transcripts are unflagged.
  - 5 flagged runs wrote the issue URL into a comment, CHANGELOG entry or test header.
  - 1 run read its own background output.
  - 1 run (fb43805788, no skill) also wrote the URL into a test header, and ran `cat tasks/*.output | tail -20`. That glob matches other agents' transcripts too, but the 20 lines it printed were unrelated test-log tails from other runs, so nothing about the TypeScript fix leaked.
- **Blind review.** A fresh agent labelled the claims, seeing only shuffled final messages with no arm and no grade.
- **Sharing.** ripgrep runs ran one at a time, and were graded only while no ripgrep agent was running. ESLint agents running at the same time share `$TMPDIR/eslint` fixtures (both arms equally).

## What this means for Recreate

Recreate's measured value is on **reproduce** and **investigate** tasks:
- no speculative production edits;
- checks that are usable as tests;
- honest "already fixed".

On **fix** tasks, it adds cost and no correctness. In this test it made fixes narrower more often.

The direction this suggests: keep Recreate for reproduction and triage, and in the fix path, stop the check from bounding the fix. One candidate wording: "fix the cause, and look for other paths to it, not just your check". That needs its own frozen test, on cases not used here.
