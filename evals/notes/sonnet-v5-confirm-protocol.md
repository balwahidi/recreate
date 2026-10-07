# Confirmatory round for v5 (frozen before any confirmatory run)

## Why

The main Sonnet run (`sonnet-v5-protocol.md`) was inconclusive under its rule. v5 won 2 pairs, lost none, and tied the rest: a net R gain of +2, below the +3 threshold.

Every v3 miss on the primary metric was an exit-status failure:

| Case | What happened |
|---|---|
| ts-60573 | the check runs `tsc`, which exits 2 by design on both sides |
| eslint-19924 | the script prints eslint's exit code but itself exits 0 |
| ripgrep-3009 | `; echo` swallows the hang |

In all three, the symptom itself was reproduced correctly. v5 had no exit-status failures. Its only misses were on ripgrep-3009, where the reporter's own test asserts a panic message that the real fix changes. Both arms hit that ceiling.

This round tests the mechanism where it can show up. It is a separate experiment, not added to the main run.

## Design

| | |
|---|---|
| Arms | v3 (`SKILL.md`, `3e89ff91…`) and v5 (`evals/variants/SKILL-v5.md`, `06a8a675…`), unchanged |
| Cases | eslint-19924 and ts-60573, 4 pairs each, `reproduce` |
| Excluded | ripgrep-3009: the reporter's assertion caps both arms |
| Pairing | both arms of a pair run at the same time |

The cases are the two where exit semantics decided pairs in the main run. This selects on the mechanism, not on individual runs: every run here is a new, independent sample.

The harness, prompt, grading, endpoints and symptom criteria are identical to the main run.

## Decision rule

Over the 8 confirmatory pairs, the net R gain is v5-only passes minus v3-only passes.

Adopt v5 only if all of the following hold:
1. The net R gain is at least 3.
2. v5's S total is at least v3's S total minus 1.
3. v5's median tokens are at most 1.5 times v3's.

The guards from the main run (P equal, H equal) already hold. If the rule fails, v3 stays, and no further rounds will be run on this question.

If v5 is adopted, the claim is limited to what was measured:
- v5 removes exit-status failures on reports whose natural check is a script or compiler output;
- across 8 case types, it lost no pair and stayed equal on discipline and honesty.

It is not a claim that v5 finds more bugs.
