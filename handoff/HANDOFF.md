Publication note: this handoff is published on branch `codex/claude-handoff-2026-10-07`. The text below records the original cloud workspace before publication. Its absolute paths are historical; use the [portable evidence bundle](recreate-claude-handoff.tar.gz) on another machine. This branch adds only the handoff package. The tested local README/SKILL edits are preserved inside the archive, not applied to the repository root. See [README.md](README.md) to start.

**Handoff: Recreate skill evaluation — 7 October 2026**

The goal is to determine whether `github.com/balwahidi/recreate` materially improves coding-agent investigations, and improve it only when measured results justify the change. The most recent experiment is complete. Its candidate did not earn adoption. There are no experiments awaiting completion and no repository change or PR to finish.

The user is transferring this project to Claude Code. This document contains evaluator knowledge, including upstream fixes: **do not give it to evaluated agents**. Claude can act as controller/reviewer; evaluated coding contexts must remain fresh and blind to fixes, other arms and results.

**User requirements that persist**

- Read the actual repository, especially `README.md`, `SKILL.md`, `cases/cases.json`, corrected `cases/*/issue.md`, `evals/prompts.py` and `evals/grade.py`.
- Do not change the skill based on plausible advice alone. Diagnose, experiment, measure effectiveness and effort, and report real numbers first. Avoid growing the skill without demonstrated benefit.
- The user explicitly requested **GPT-6.1 Sol, medium effort** for evaluated coding agents, with the controller reviewing their work. If Claude Code cannot run that model through an available harness, say so; do not silently substitute Claude and combine its scores with these results.
- For choosing new tests, use the skill's claims and issue snapshots, not old successful scores. The original selection restrictions excluded `docs/results.md`, `evals/results/` and prior conclusions. Reading the completed experiments below is for continuity and diagnosis; it does not make reused cases untouched holdouts.
- Evaluated agents must not see historical resolutions, fixing PRs or post-report discussions. The controller may use hidden real upstream production fixes for grading. The user specifically supplied pnpm PR 16221 for this investigation.
- Match model, settings, tools, revision, dependency seed and budget within pairs; randomize order; use clean independent checkouts and fresh contexts; preserve final messages, patches and reproduction commands.
- Inspect the actual symptom and production edit order. Related failures, setup errors, unjustified flaky claims, relabeled simulations and blanket abstention do not establish success.
- Do not open a PR or modify the Recreate repository without an explicit request. This handoff creates files outside the repository only. Preserve existing local work.
- The user prefers autonomous completion of authorized work and dislikes repeated confirmation requests. Do not restart completed work or treat every routine action as requiring approval. Do not append runs to a frozen experiment or silently replace failed contexts.

**Repository state**

Repository: `/workspace/recreate`, upstream `https://github.com/balwahidi/recreate`, local HEAD `3eac7ee5902b4f06cb1b043c693f325af09dbca7`.

`git status --short` currently shows modified `README.md` and `SKILL.md`. These edits predate the two experiments described here. Both experiments preserved them; “skill unchanged” means unchanged from the tested working copy, not a clean Git checkout. Do not reset them.

The tested current skill is 291 whitespace-delimited words. Its SHA-256 is:

```text
f0bb40aa76f2dd82a5db91975ecf9a45fc408653db7d9ce12856019a4cd6f034
```

The portable bundle includes the exact current README/skill, prompt/grader source, case registry, corrected issue snapshots, Git HEAD/status and a patch of the pre-existing local changes. Cloning GitHub alone may not recover the tested working copy. On another machine, compare the snapshot and patch before applying anything; preserve any work already present there.

**Where the evidence lives**

| Item | Original workspace path |
| --- | --- |
| Earlier pnpm on/off experiment | `/workspace/recreate-pnpm-16221-20261007` |
| Latest current/candidate experiment | `/workspace/recreate-simulation-experiments-20261007` |
| Latest report | `/workspace/recreate-simulation-experiments-20261007/report.md` |
| Latest frozen protocol and rubric | `plan.json`, `rubric.json` in that directory |
| Per-run adjudication and timing | `review.json`, `metrics.json` |
| Artifact/prompt/skill integrity checks | `verification.json`, `verify.py` |
| Unimplemented next-test proposal | `next-experiment.md` |
| Environment recipe | `setup/environment.md` in each experiment |
| Portable evidence | `/workspace/recreate-claude-handoff.tar.gz` |

The archive has a top-level `recreate-claude-handoff/` directory. It contains this handoff, `repository-state/`, and `evidence/` with the two experiment directories. `MANIFEST.json` records SHA-256 and size for each payload file. It includes controller results, original agent artifacts and command telemetry, probes, patches, logs and protocol helpers. It excludes dependency stores, Git databases, full target checkouts, build caches and executables. Reports' relative evidence links should work within the extracted evidence directories.

The archive is portable **audit evidence**, not a ready-to-run environment. Helper scripts and saved telemetry contain original absolute paths. Rebuilding on another machine requires adapting controller paths and restoring pinned sources/tools/dependencies; do not edit archived agent artifacts or original scores. Some setup and probe source directories still exist only in the original workspace.

**Experiment 1: pnpm skill off versus on**

Six fresh GPT-6.1 Sol/medium contexts, three randomized pairs, all `pnpm-16217 / investigate`, 600-second budgets. Original report: `recreate-pnpm-16221-20261007/report.md`.

| Outcome | Off | On |
| --- | ---: | ---: |
| Reproduction fails before and passes after real fix | 0/3 | 0/3 |
| Production edited before faithful platform reproduction | 3/3 | 0/3 |
| Returned patch causes verified POSIX dispatch regression | 3/3 | 0/3 |
| Matching Node failure through explicitly labeled decoding simulation | 0/3 | 3/3 |
| Median seconds to saved result, excluding setup pause | 231 | 298 |

Controls added BOMs without the necessary Windows guard and claimed a fix after BOM-byte checks. Controller review verified `ENOEXEC`/errno 8 from actual generated shims on Linux; baseline and real fix dispatched correctly. This check used a stand-in `pwsh` to test kernel shebang dispatch, not a PowerShell interpreter.

Skill-on agents preserved production code and produced useful decoding demonstrations, but generated shims on Linux. The real Windows-only fix therefore did not resolve their artifacts. The result supports a narrow investigation-discipline benefit, not successful faithful reproduction or broad effectiveness. Three same-direction paired discipline outcomes are a tiny sample (reported two-sided sign-test p=0.25).

There was a dependency-relocation setup interruption in the first three contexts; the frozen accounting excludes a 79.5-second setup pause and documents restoration before source edits. Some controls also lacked lint/formatter dependencies. Review `setup/incident.json` and the report before using its timing numbers. Some redundant generated caches were later removed, but source, patches and logs were preserved.

The earlier report calls the one-rule candidate “untested.” **That statement is historical and is superseded by Experiment 2.**

**Experiment 2: current skill versus one-rule candidate**

Both arms had Recreate enabled. This was not another on/off test.

Current rule:

> If you simulate a condition you can't match (such as another OS), call the result simulated.

Candidate replacement:

> Label simulations. They must exercise the reported environment's production path and matching failure; otherwise report partial evidence.

Word count: 291 → 292. Candidate SHA-256:

```text
4f22cc69b2f6afaaf87ba37a3372c3b1cf2e3da98809533f99925abeff58a9f2
```

The text was frozen before reading the ESLint transfer report. Twelve contexts were attempted: three pnpm pairs at 480 seconds, three ESLint pairs at 300 seconds. Same GPT-6.1 Sol/medium, no inherited conversation, identical conditions within each pair, at most three active coding contexts. Pair orders were randomized in advance; all three ESLint pairs happened to run candidate first. No exploratory replacements, extra cases or wording changes were added.

Eleven contexts completed and saved artifacts within budget. One current-skill ESLint context was stopped by a platform cybersecurity-risk filter after partial work; it has no final result and was not replayed or replaced. This is an infrastructure interruption, not a skill failure.

| Pair | Case/task | Current run | Candidate run | Command exits current / candidate, before → after fix | Frozen-primary verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | pnpm-16217 / investigate | `937c2684ddb9` | `84c573db070c` | 1→1 / 1→1 | Tie, both miss primary |
| 2 | pnpm-16217 / investigate | `8a11bee1da01` | `904163b46b12` | 1→1 / 1→1 | Tie, both miss primary |
| 3 | pnpm-16217 / investigate | `303ed57dde7a` | `90e55fddaa79` | 1→1 / 1→1 | Tie, both miss primary |
| 4 | eslint-19924 / investigate | `10304b9c0f82` | `41768decd51b` | 0→1 / 0→1 | Tie, command convention mismatch |
| 5 | eslint-19924 / investigate | `8deba87f9d49` | `871525beacdf` | Platform error / 1→0 | Inconclusive; exclude pair |
| 6 | eslint-19924 / investigate | `7ab64eb1b6b0` | `6fa450bf5532` | 2→0 / 0→1 | Current win on command convention only |

Paired primary scores: pnpm **0/3 versus 0/3**; ESLint **current 1/2 versus candidate 0/2**. Zero candidate wins, four ties, one current command-convention win, one inconclusive pair. Do not count the unmatched candidate success as a paired win.

Symptom-level ESLint evidence ties at **2/2 in both comparable arms**. All five completed ESLint artifacts reach real CLI write-stage EMFILE under a finite Linux descriptor limit; the upstream fix resolves it. Three harnesses return 0 when they detect the bug, then 1 when it disappears. Thus their production observations are valid while their command convention fails the frozen primary grading criterion. Preserve both facts.

The output prompt asks for a command that demonstrates the bug; it does not explicitly specify the grader's nonzero-before/zero-after convention. The unchanged grader labels 0→1 as `fails_both`, despite the pre-run returning zero. **Read raw exits and logs, not that label literally.** No artifact was repaired or retroactively scored as a primary pass.

All eleven completed agents labeled simulations and left production unchanged. No setup pause occurred in this experiment. Comparable-pair median seconds to saved artifact: pnpm current 247.422 / candidate 279.748; ESLint current 197.7135 / candidate 240.8885. The candidate did not demonstrate an efficiency benefit. These are elapsed times, not tokens or dollar costs.

The frozen adoption gate required three repeated pnpm primary improvements and no material transfer regression. The candidate achieved zero pnpm improvements and was rejected. It exists only as an experimental snapshot; it was not installed in the repository.

**Mechanism established by controller diagnostics**

pnpm report 16217 describes Windows PowerShell 5.1 interpreting BOM-less UTF-8 and corrupting the `工具/cli.js` path into the reported mojibake, causing Node `MODULE_NOT_FOUND` instead of `CJKTOOL OK`. Console OEM code page 437 does not determine the ANSI decoding code page; Windows-1252 matches the reported corruption. The original issue already supplies the encoding diagnosis/BOM workaround, so this is not a test of discovering an unknown cause.

All six Experiment 2 agents used the Linux generator, then modeled legacy decoding. Before the fix, this produces the same relevant bytes as Windows. After the legitimate fix, Linux still emits BOM-less scripts to preserve POSIX shebang behavior. Merely calling the actual function and observing a matching pre-fix error therefore does not establish environment fidelity.

The hidden controller's TypeScript probe configures the platform input before module initialization, models decoding, and invokes real Node:

| Modeled generator | Decoder | Before fix | After fix |
| --- | --- | --- | --- |
| Windows | Legacy Windows-1252 | Fail | Pass |
| Windows | UTF-8 | Pass | Pass |
| Linux | Legacy Windows-1252 | Fail | Fail |
| Linux | UTF-8 | Pass | Pass |

Evidence: latest `controller/feasibility/component-matrix.json`, `probe.mjs` and logs. These eight controller invocations are diagnostic checks, not coding-agent runs or proof that alternative wording works. Native Windows/PowerShell was not executed.

A separate ESLint feasibility probe calls actual `ESLint.outputFixes` with 1,000 real files and descriptor limit 128: EMFILE before, 1,000/1,000 correct writes afterward. This proves useful Linux investigation is feasible without simulating a whole Windows OS. Evidence: latest `controller/feasibility-eslint/`.

**Pinned sources and replay mechanics — evaluator only**

| Case | Starting revision | Real fix |
| --- | --- | --- |
| pnpm-16217 | `66cc12fa918c34b15a1928dde5233f0fc343f44d` | `a9d33c9d1a2affc11d23a50a5bd0e20c7dd8b08a`, PR 16221 |
| eslint-19924 | `35cf44c22e36b1554486e7a75c870e86c10b83f8` | `07fac6cafa0426b4d1ea12d9001f3955f19b286d` |

pnpm production patch: earlier `controller/upstream-production.patch`. It guards the BOM on Windows in TypeScript and Rust. ESLint patch: latest `controller/eslint-upstream-production.patch`; it retries EMFILE/ENFILE with concurrency 100 around the write path.

Each `runs/<id>/controller/` preserves `final-message.md`, `agent.patch`, `actual-final.patch`, `run-command.txt`, `result.json`, `command-summary.json`, `trace-review.txt`, projections and `replay/` logs/JSON. `workspace/.telemetry/` contains recorded commands, before/after tracked diffs and output logs. The interrupted run has `agent-error.txt` and a partial final-tree capture, not an invented agent result.

`replay.py` uses a frozen copy of repository `evals/grade.py` with case/environment adapters, preinstalled identical dependencies and only genuine upstream production hunks. pnpm's TypeScript output is rebuilt on both sides. If an investigation changed production, the protocol additionally removes whole production-file diffs without repairing the remaining reproduction. In Experiment 2 every completed projection equals the full artifact. Never run two replay processes for the same case concurrently: they reuse a controller checkout. Do not replay on agent workspaces.

On the original workspace, these checks do not launch agents or new evaluation runs:

```sh
python3 /workspace/recreate-simulation-experiments-20261007/verify.py
python3 /workspace/recreate-simulation-experiments-20261007/metrics.py
```

They most recently verified twelve prompt/context records, eleven matching saved artifacts, one preserved error, the exact frozen skill and unchanged prompt/grader source. Verify paths before using helpers elsewhere. Do not invoke `prepare.py` on the existing completed experiment: its plan is intentionally frozen.

Host: Linux x86_64, Node 24.19.0, npm 11.9.0. pnpm has repository-managed Node 26.10.0, pnpm 12.7.0, Rust 1.97.0 and cargo-nextest 0.9.146. No Windows PowerShell or PowerShell Core. See environment recipes for exact commands, caches, baseline checks and setup limitations. Baselines: 80 pnpm TypeScript tests, 170 Rust tests with one skipped, six ESLint outputFixes tests. ESLint has no tracked lockfile at this pin, so resolving dependencies anew can drift.

**What to do next, and what remains unproven**

1. Audit the latest report against a few representative artifacts before accepting the conclusions: pnpm's persistent post-fix error, ESLint's inverted harness, and the successful minimized ESLint command. Keep observations and primary grading separate.
2. The cheapest proposed evaluation change is a shared prompt instruction: the saved command must exit nonzero when expected behavior fails and zero when it succeeds, with setup errors reported separately. Apply identically to future arms. The mismatch is proven; whether this instruction reliably changes agents remains untested. It belongs in the common harness, not as unearned skill text. No repository change implementing it has been made.
3. The best next skill hypothesis is procedural: locate where production reads a missing environmental condition, model it at that boundary before initialization, and verify the effective value. Test on an unseen environment-dependent issue with a hidden real fix and a transfer concern about needless abstention. Freeze exact wording, endpoints, cases, count, budget and promotion threshold before outcomes. Do not claim repeated pnpm success would establish general effectiveness.
4. Keep candidate development outside SKILL.md until it demonstrates useful improvements with acceptable effort. The latest abstract sentence failed. Do not keep appending advice to rescue it after seeing results.

`next-experiment.md` expands these proposals. They are not implemented or validated. Another untested concern is that the candidate requested “partial evidence” while the unchanged status menu lacked a partial-reproduction option; a label change alone would not solve the demonstrated generator-state error.

Limitations to retain in any future summary: two issue families, small samples, controller review unblinded, shared host/caches, dependency differences from reporters, no native Windows runner, one interrupted transfer pair, and a development case already known to expose a gap. Already-fixed reports, near-miss input substitutions and scheduling-sensitive flake-rate measurement remain untested in these two batches. These results reject one candidate and show a narrow discipline benefit in the earlier on/off test; they do not prove broad Recreate effectiveness or ineffectiveness.

Do not restart the old five-case Stage 1/Stage 2 plan from early conversation history. The user subsequently directed the pnpm investigation and these targeted follow-up experiments; those completed protocols are the relevant current state. Any future experiment is a new protocol, not an extension or replacement hidden inside the old twelve-context count.
