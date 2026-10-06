# Research: does Recreate add anything?

Snapshot of the reproduction/debugging skill landscape (October 2026) and what it implies for Recreate's scope. Claims about *behavior* below are hypotheses until the evals in `evals/` measure them.

## Comparable work

| Project | What it already does | Overlap with Recreate | Where it diverges |
|---|---|---|---|
| Matt Pocock `diagnosing-bugs` (~1.4k words) | Phase 1 "build a feedback loop" that asserts the user's exact symptom; ladder of loop types (test → curl → CLI → browser → bisect → differential → HITL); repro-rate for flaky bugs; then hypothesise, instrument, fix, regression-test, clean up. | High on the reproduction phase itself. | Full debugging workflow; reproduction is a means to a fix. No first-class "not reproduced" outcome. |
| Superpowers `systematic-debugging` | "No fixes without root-cause investigation first"; reproduce consistently, check recent changes, trace data flow, hypothesis testing, 3-failed-fixes escalation. | Low. Reproduction is one bullet. | Root-cause methodology, not reproduction fidelity. |
| `silkyland/reproduce-my-bug` (~1.5k words + references) | Reproduce-only, never fixes; flaky handling; REPRO.md dossier with evidence log. | Highest. | Encourages code-path tracing and ranked hypotheses *before* reproducing, and produces a large dossier. Both conflict with Recreate's principles 1 and output design. |
| SWE-agent / OpenHands default prompts | "Create a script to reproduce the error and execute it" as step 1 of issue resolution. | "Reproduce first" is already standard agent behavior and heavily trained in. | Any failing script counts; no symptom-fidelity check, no environment matching, no not-reproduced path (the task always ends in a patch). |
| Verification/proof skills (e.g. Superpowers `verification-before-completion`) | Require evidence before claiming success. | Shares the "evidence over claims" stance. | About verifying fixes, not establishing the bug. |

## Benchmarks and research

- **SWT-Bench** (Mündler et al., 2024): issue → reproduction test, graded fail-to-pass against the real fix. Shows test generation from issues is hard (low tens of percent) and that code agents beat dedicated test generators. Grading method adopted here.
- **AEGIS, ReProAgent, DPIAgent, Otter**: agent systems specialised for reproduction tests. They rely on scaffolding (search tools, iterative execution feedback), not on prompts alone. Recreate stays a prompt.
- **SkillsBench**: evaluates skills as paired runs with and without the skill, with mechanical verifiers and holdouts. The design in `docs/methodology.md` follows it.

## What would be duplicated

- Telling a frontier agent to reproduce before fixing. Agents already do this when asked to reproduce. The control prompt says the same thing, so this instruction should show no gain and is excluded unless the baseline says otherwise.
- Reteaching the reproduction ladder, bisect, instrumentation or test frameworks.
- Hypothesis ranking and dossiers (reproduce-my-bug) and fix workflows (diagnosing-bugs).

## Candidate differentiators (to be measured)

1. **Symptom fidelity.** Count a reproduction only when the observed behavior matches the reported one, not merely when something fails.
2. **Relevant-environment matching.** Match the conditions that plausibly affect the symptom (version, OS, runtime, config), and say which differences remain.
3. **Repository-native mechanism.** Put the repro where the project puts regression tests.
4. **Production code untouched.** No speculative fixes during reproduction.
5. **Not reproduced is a result.** Recognise already-fixed, reporter-misunderstanding and missing-information cases, and ask for the one missing piece.
6. **Flaky cases.** Measured rates instead of a single pass/fail.
7. **Short report.** The output contract in the brief, not a dossier.

Each is kept in `SKILL.md` only if the control baseline shows the failure it targets and an ablation shows that removing it hurts.

## Outcome

Results are in `docs/results.md`.

| Candidate | Control already does it? | In the shipped skill? |
|---|---|---|
| 1. Symptom fidelity | Mostly. It slips when a nearby variant still fails. | Yes. Together with the already-fixed rule, this fixed variant substitution. |
| 2. Environment matching | It simulates on its own, but presents the result as native. | Partly. Only the "call it simulated" clause, because general parity guidance had no measured effect. |
| 3. Repository-native mechanism | Often. | No. The instruction had no measured effect. |
| 4. Production code untouched | Yes on "reproduce" prompts. No on "investigate" (9/10 edited) or "fix" (edited before reproducing). | Yes. This is the largest effect. |
| 5. Not reproduced / already fixed / as designed | Already-fixed: inconsistent. As designed: no. | The already-fixed rule, yes. The as-designed rule was dropped because it changed nothing in 4 clean runs. |
| 6. Flaky rates | No. | Yes. |
| 7. Short report | Reports are already short, about 300 words. | Yes. A status line and labelled fields, at the same length as the control. |

