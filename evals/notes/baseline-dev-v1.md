# Baseline (control, no skill), dev cases, run baseline-dev-v1

Child Devin sessions, same model and harness as the treatment arm. One run per case and task. Each session took about 6 minutes. The audit found no visits to the issue page or fix PR, and no browser use.

| Case | reproduce: outcome | reproduce: production files touched | investigate: production files touched |
|---|---|---|---|
| eslint-19245 | reproduced, standalone script at repo root (not in the rule's test file) | none | rule changed (fixed) |
| vue-12294 | reproduced, new spec file in the native test dir | none | watch.ts changed (fixed) |
| eslint-19924 | reproduced with `ulimit -n 1024` + 5000 files, report's stack trace matched | none | eslint.js changed (fixed) |
| urfave-cli-2176 | reproduced, goroutine test panics within ms, report's trace matched; no rate measured | none | command.go and command_setup.go changed (fixed) |
| eslint-19818 (works as designed) | "reproduced the bug", "bug is wider than the report says", 7 cases "clearly used" | none | rule changed ("Confirmed and fixed") |

## Observations

- On the explicit reproduce prompt, the control already reproduces before theorising, matches the report's stack and symptom, and leaves production code alone. "Reproduce first" and "don't modify production" add nothing on this prompt.
- **Failure 1, observed behavior accepted as a defect.** On eslint-19818 the control reproduced the reported output faithfully, but then asserted that it was a bug and widened the claim, without checking the rule's documented semantics. Maintainers closed it as working as intended. The investigate arm "fixed" it.
- **Failure 2, investigate prompt goes straight to fixing.** 5/5 changed production code (expected for that prompt). This is where a skill could change behavior, if it is invoked.
- **Minor:** eslint-19245 used a root-level script rather than the rule's RuleTester file. urfave-cli gave no reproduction rate for a race. Reports run 200–450 words and mix in root-cause analysis ("Where to look", "Likely cause").
- The dev set was too easy to separate the arms. Two cases were added for kinds the control has not yet faced: a platform-specific bug on the wrong OS, and an already-fixed bug.

## Run baseline-dev-v2 (two added dev cases, reproduce task)

| Case | Outcome |
|---|---|
| eslint-20209-fixed | The report's exact snippet does **not** fail on this revision, and the agent confirmed it does fail on 9.37.0. It then searched for other variants that still break, and opened with "I reproduced the bug". |
| eslint-18575-windows | Monkey-patched `node:path` to `path.win32` and opened with "I reproduced it on Linux by simulating Windows path handling". The simulation is disclosed. The reproduction is plausible but not faithful. |

- **Failure 3, substitution.** When the reported case did not fail, the agent replaced it with a related failure and labelled the result as reproducing the reported bug. Together with Failure 1, this is the core symptom-fidelity gap.
- **Failure 4, minor.** Simulated environments are reported as plain reproductions, with the caveat buried inside.

# Treatment v0 (SKILL.md v0, 352 words), dev cases, run treatment-dev-v0

| Case | reproduce: control → treatment | investigate: production files touched (control → treatment) |
|---|---|---|
| eslint-20209-fixed | "reproduced" (substituted variant) → **Reproduced on 9.37.0 only (already fixed)**, with the version where it changed (10.1.0) | n/a → none; "already fixed" |
| eslint-18575-windows | "reproduced" (simulated, caveat buried) → **Reproduced (simulated Windows)** | n/a → none |
| eslint-19818 | "bug, wider than reported" → "Reproduced", plus a "Whether this is a bug" section that cites the documented dead-store semantics and the existing `x = x++` test, and calls it ambiguous | fixed → none; "working as designed" |
| urfave-cli-2176 | reproduced, no rate → reproduced, **11/200,000 subtest runs** | fixed → none |
| eslint-19245 | standalone script → **RuleTester valid cases in the rule's own test file** | fixed → none |
| eslint-19924, vue-12294 | reproduced → reproduced, with reliability and the reporter's version checked | fixed → none |

- All four observed failures are addressed on dev. With n=1 per cell this is a signal, not a measurement. Holdout is next.
- Investigate prompt: production edits went from 5/5 to 0/7. Whether that is desirable depends on the user's intent. A `fix` task was added to holdout to check that the skill does not block a fix that was actually requested.
- Report length did not shrink (225–352 words vs 200–450). "Likely cause" paragraphs remain, despite the "one-line pointer" rule.
- v0 is frozen (`evals/notes/SKILL-v0.md`) for the holdout run. No tuning before holdout.

# Repeats (run repeat-v0, 3 more samples per arm; counts below include the original sample, so n=4)

| Case | control | treatment v0 |
|---|---|---|
| eslint-20209-fixed (already fixed, related variants still fail) | 4/4 open with "reproduced", citing a substituted variant | 4/4 "Reproduced on 9.37.0 only (already fixed)" |
| eslint-19033-fixed (already fixed, no nearby variant) | 4/4 correctly say it doesn't reproduce at the checkout, only on the releases | 4/4 same |
| eslint-18575-windows (Windows-only) | 4/4 "reproduced", simulation disclosed in the first sentences | 4/4 "Reproduced (simulated Windows)" |
| eslint-19818 (works as designed) | 4/4 call it a bug | 4/4 status "Reproduced". Only the first sample discussed intent. The rule "check documented intent" had no measurable effect |

- Robust effect: the skill prevents **substitution**. When the exact report doesn't fail but related variants do, the control presents the variants as the reproduction every time; with the skill, the result is reported as "already fixed".
- No effect where the control is already right (19033). The simulated-environment effect is labelling only.
- The intent rule did not work. v1 rewords it once, as a status rule. If it still doesn't move 19818, it gets removed.

# v1 probe (rule reworded as a status rule): run treatment-v1-probe

- eslint-19818: 3/3 still report "Reproduced" and call it a bug. Across 7 treatment samples the intent rule had no effect, so **it was removed** (v2). Judging design intent from docs is not something a short instruction reliably changes.
- eslint-20209-fixed: 3/3 "already fixed", so the effect held. Treatment total is 7/7, control 0/4.

# Ordering: production edits before any reproduction ran (holdout, from session event timelines)

| Session | Production edit before reproduction ran? |
|---|---|
| eslint-19033-fixed control investigate | **yes**: edited `lib/rules/no-lonely-if.js` (+36 lines) before `npm install` finished, then found it already fixed and reverted |
| eslint-19957 control fix | **yes**: rule edited at 19:06:52, before dependencies were installed. Tests ran afterwards |
| vue-13611 control fix | **yes**: `componentSlots.ts` patched before `pnpm install` completed |
| eslint-19637 control investigate | no: test added and run first |
| pydantic-11849 control investigate | no: repro script showed the bug, then the fix |
| eslint-19957 treatment fix | no: CLI reproduction (exit 1) at 19:07:19, then the edit |
| vue-13611 treatment fix | no: tests written and run, then the fix |
| treatment investigate (3) | no production edits at all |

Control 3/5 vs treatment 0/5 production edits before reproduction, on prompts that allow edits.

# Ablation (run ablation-v2: treatment = v2 skill, minimal = v2 without the environment/simulation, native-test, and flaky-rate rules, control = no skill; n=2 per arm)

| Case | control | minimal | v2 |
|---|---|---|---|
| eslint-20209-fixed | 0/2 already-fixed (substitutes variants) | 2/2 | 2/2 |
| urfave-cli-2176: per-iteration rate stated | 0/2 | 0/2 (one said "4 of 4 runs failed") | 2/2 (1 in ~4,000; 111/320,000) |
| eslint-18575-windows: "simulated" in status | 0/2 (disclosed in body) | 0/2 (disclosed in body) | 2/2 |
| eslint-19245: repro in the project's test suite | 0/2 | 0/2 | 0/2 |
| eslint-19637 investigate: production edited | 2/2 | 0/2 | 0/2 |

Decisions for v3:
- Keep the substitution and already-fixed rules, the production-unchanged rule, and the stop rule. The minimal skill already carries their effects.
- Keep the flaky-rate rule. Removing it loses the rate (pooled with the dev-v0 run: v2 3/3, minimal 0/2, control 0/3).
- Shrink the environment rule to the one clause that changed behavior, "call the result simulated". The "match relevant conditions" part changed nothing measurable.
- **Remove** the native-test rule: 0/2 here, and mixed on holdout (treatment more native on eslint-19957, less on pnpm-10290).

# Contamination and clean reruns

The evaluated sessions shared a persistent memory store. From 19:11, some of them saved case notes to it, including root causes and a rule that varied by whether the skill was present. Runs that started after those notes existed are excluded: `treatment-v1-probe`, `ablation-v2` and `holdout-v3`, along with the tables above that came from them. Every prompt now says not to read or write memory. Before each rerun I checked that memory was clean, and that no evaluated session touched it.

# Ablation, clean (run ablation-v2b: v3 skill vs minimal vs control, n=2)

| Case | control | minimal | v3 |
|---|---|---|---|
| eslint-20209-fixed: already-fixed, no substitution | 0/2 | 2/2 | 1/1 (the workflow reused one session for both repeats) |
| eslint-18575-windows: "simulated" in the status line | 0/2 (said in the body) | 2/2 | 2/2 |
| urfave-cli-2176: rate stated | 0/2 | 1/2 ("5 of 5 runs") | 2/2 (9/100,000 subtests; 20/20 invocations) |
| eslint-19637 investigate: production edited | 2/2 | 0/2 | 0/2 |
| eslint-19245: test added to the project's suite | 2/2 | 0/2 (`tests/repro/` and a standalone script) | 0/2 |

Decisions for v4:
- **Remove the simulated-environment rule and its status.** The minimal skill, which doesn't have the rule, labels the simulation anyway, so the symptom-fidelity rule carries that effect.
- **Keep the flaky-rate rule.** Pooled clean data: v0–v3 3/3 give a rate, control 0/3, minimal 1/2 (a coarse one).
- **Native tests: the skill doesn't help, and may push agents toward standalone scripts.** On eslint-19245 the control used the suite 2/2 and both skill variants 0/2. On holdout-v3b the v3 skill used native tests for vite, TypeScript, vue and eslint-19957. That's mixed, and adding the native-test rule back had no measured effect before, so v4 doesn't add one.

# v4 check (run simulated-v4: v3 without the simulated rule, n=2)

eslint-18575-windows: 1 of 2 runs said "simulated" in the status line. r2 opened with "Reproduced (at 4f08332 …)". pnpm-10216-windows: r2 found the bug isn't Windows-specific, which is correct. r1 didn't mention Windows.

Pooled clean labelling: with the rule 6/6, without it 3/4 (minimal 2/2, v4 1/2), control 0/6. That costs 17 words for a small, consistent gain, and v3 is also the version the holdout-v3b run used. **v3 is the shipped skill.**

# Holdout replay: control repeats (run holdout-control-r, n=2 on the 4 cases where the arms differed)

Replay passes (the reproduction fails before the fix and passes after it):

| Case | Control (v0 + r1, r2) | Skill (v0, v3b) |
|---|---|---|
| eslint-19957 | 1/3 | 2/2 |
| pnpm-10290 | 1/3 | 2/2 |
| ts-60573 | 1/3 | 2/2 |
| pydantic-11849 | 0/3 | 1/2 |

The control's failures are real symptoms with unfaithful artifacts. On the replay itself the arms differ: the matched holdout-v0 run gives control 4/8 vs skill v0 7/8. These control repeats were drawn only on cases where the arms differed, so they are not pooled into that comparison. v3 was tuned partly on holdout-v0. Details are in docs/results.md.
