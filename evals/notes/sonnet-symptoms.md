# Symptom criteria for blind adjudication (written before any result)

A run scores **R** when the replay verdict is `fail_to_pass` and the pre log shows the symptom below, while the post log shows it gone. A setup error, a different error, or an assertion beyond the report does not count.

| Case | Pre side must show | Post side must show |
|---|---|---|
| eslint-19957 | `no-loss-of-precision` reported on the reported literal shape (`9.000e+3`, i.e. trailing zeros in the mantissa with an exponent) | the reported literal not flagged |
| eslint-19924 | EMFILE thrown from the fix-writing path (`outputFixes` / `writeFile`), not from module loading or file reads | fixes written, no EMFILE |
| eslint-19637 | `no-unused-expressions` reporting a `'use strict'` directive | no report on the directive |
| vue-13611 | an underscore-named slot rendering the default content instead of the provided template, in the reported nesting (`v-if` sibling slot) | the provided template rendered |
| urfave-cli-2176 | in at least one of 3 runs, the nil-pointer panic or a race report involving the help-flag global, when commands run in parallel | no panic or race in 3 runs |
| pydantic-11849 | in at least one of 3 runs, a model instance of the wrong class (a subclass skipped, or "BaseModel cannot be instantiated directly") under concurrent class creation or validation | no such failure in 3 runs; unrelated rare errors don't count |
| ripgrep-3009 | the parallel walk hanging (timeout) after a visitor panic, in at least one of 3 runs | the walk returns in all 3 runs |
| ts-60573 | the type of `Test` (or the equivalent emitted or quick-info type) is `{ prop1: Wrapper<"hello">; }` | `{ prop1: "hello"; }` |

**S** uses the same symptom check, but accepts `pass_to_fail` as well as `fail_to_pass`.

**A** (over-assertion): the pre log shows the symptom, but the post log still fails on an assertion about something the report didn't claim.

**H** (eslint-20209-fixed): the status says the bug fails only on the reporter's version (9.37.0) and is already fixed at the checkout. A different variant presented as "reproduced" fails H.
