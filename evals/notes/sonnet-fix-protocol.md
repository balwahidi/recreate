# Fix test: v7 vs no skill on "Fix this bug." (frozen before any run)

## Question

Do agents with Recreate produce correct fixes more often than agents without it? "Correct" is judged by the upstream fix's own tests, which the agent never sees.

So far every Sonnet test used "Reproduce this bug" or "Look into this bug report". Most people ask an agent to fix a bug, and this is the first test of that case.

## Cases: five, chosen for grading quality, not count

Each case's grader was checked before any run: it fails at the checkout, and it passes with the upstream fix twice in a row. A sixth valid grader, eslint-19637, is held in reserve and not used. Results are in `evals/results/fix-validate/`.

| Case | Hidden tests (from the upstream fix) | Also run (existing neighbours) | What a wrong or partial fix trips |
|---|---|---|---|
| eslint-19957 | 3 new valid literals in the rule's test file | the rest of `no-loss-of-precision` tests | a fix limited to the reported literal, or one that stops flagging real precision loss |
| eslint-19924 | `tools/check-emfile-handling.js` running `--fix` on ulimit+1 files, `ulimit -n 1024` | `tests/lib/eslint/eslint.js` | a fix that doesn't hold under real EMFILE, or that breaks `outputFixes` |
| vue-13611 | underscore slot names (`_foo`, `_inner`) at runtime | the rest of `componentSlots.spec.ts`, and compiler `vSlot.spec.ts` | a template-only workaround; a fix that exposes internal slot keys |
| ts-60573 | new compiler and fourslash baselines for the reported type | every `declarationEmit` and `isolatedDeclaration` test | a wrong printed type; a too-broad change to node reuse that alters other declaration output |
| ripgrep-3009 | `panic_in_parallel` (the report) and `panic_in_parallel_builder` (a panic in the visitor builder, not in the report), 3 runs | every `ignore` lib test | a fix for the visitor panic only; a fix that still hangs sometimes |

The agent's whole patch is applied. Then the upstream test files are checked out on top, overwriting the agent's own edits to those files. The ripgrep tests are appended to `mod tests` under `hidden_` names.

## Arms and runs

- **none:** no skill.
- **v7:** `SKILL.md` as shipped (SHA-256 `5c454b0c…3f7d`), given the same way as in earlier tests.

Both arms get the same prompt, ending in "Fix this bug." The earlier prompts also asked for the command that demonstrates the bug. That request is removed here, because it would nudge the no-skill arm toward writing a reproduction.

There are 2 pairs per case, so 10 pairs and 20 runs. Both arms of a pair run at the same time. Exception: ripgrep runs go one at a time with nothing else on ripgrep, after the cross-run kills seen in the v7 test.

## Endpoints

- **F (primary):** the patch applies and the grading command exits 0 on every run.
- **Overclaim:** the final message says the bug is fixed, but F is false.
  - A fresh agent judges each final message blind: shuffled, with no arm and no grade. The labels are `verified` (claims fixed and cites a check it ran that now passes), `unverified` (claims fixed without one) and `not_fixed` (says it's not fixed, or only partly).
- **Regression test:** the agent's patch adds or changes a test.
- **Cost:** median tokens, tool calls and time.

## Decision rule

With 10 pairs this can only show a large difference, and ties are expected on easy cases.

- **"Recreate fixes better":** v7-only F pairs minus none-only F pairs is 3 or more, with at most 1 none-only pair.
- **"Recreate fixes worse":** none-only pairs minus v7-only pairs is 2 or more.
- **Otherwise:** no difference in fix correctness. The secondary endpoints are then reported as the result, without a claim of superiority.

Cost is reported, not gated. A fix that reproduces first is expected to cost more.

`SKILL.md` doesn't change on this test. It is a measurement of the shipped skill.

## Amendment (grader only, written after launch but before any run finished or was graded)

1. **Only upstream's tests and tests that existed at the checkout run.**
   - The first grader also ran tests the agent itself added in the touched files and crates. A correct fix could then fail on its author's own over-strict test, and that would bias against whichever arm keeps more tests.
   - Now neighbouring test files are restored to the checkout before grading:
     - `tests/lib/eslint/eslint.js`;
     - `vSlot.spec.ts`;
     - TypeScript's `tests/cases` and `tests/baselines/reference`.
   - ripgrep runs its 147 pre-existing lib tests and the 2 hidden ones by exact name (`evals/sonnet/ripgrep-3009-base-tests.txt`).
2. **Every grading command runs with a private `TMPDIR`.** ESLint's test suite copies fixtures to `$TMPDIR/eslint`. Agents running at the same time use that path too, and one revalidation of eslint-19924 failed with the upstream fix because of it.

All five graders were revalidated after this change: each fails at the checkout and passes twice with the upstream fix.

Agents themselves still share `/tmp`. ESLint agents running at the same time can disturb each other's ESLint test runs. Both arms run under the same conditions.
