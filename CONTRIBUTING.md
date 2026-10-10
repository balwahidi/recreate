# Contributing

`SKILL.md` is the product, so treat a change to its instructions like a code change that needs evidence.

Recreate only reproduces bugs. Changes that make it fix bugs are out of scope: three tests (`evals/notes/sonnet-fix-results.md`, `sonnet-fix2-results.md`, `haiku-37762-arms-results.md`) found no gain from steering the fix.

## Proposing an instruction change

1. **Name the failure.** Give a case and a transcript where an agent with the current skill does the wrong thing. Instructions that sound good but come with no observed failure aren't accepted.
2. **Make the smallest edit** that targets that failure. Rewording an existing rule is better than adding one.
3. **Run it on the dev cases.** Run the case, at least 3 repeats with the new skill and 3 with the old one, plus the usual neighbours. The arms are configured in `RUN` and `SKILLS` in `evals/workflow.py`.
4. **Ablate.** If a rule doesn't change behavior across repeats, remove it. Several rules were dropped this way (see `docs/results.md`).
5. **Check the holdout split** only after freezing the text. Don't tune on holdout cases; move a case to dev if you have to.
6. **Size.** Report the word count of `SKILL.md`. Growth is a regression unless the results pay for it.

## Running evals

- `evals/sonnet/` runs evaluated agents as Sonnet subagents with frozen plans, transcript audits and blind review (see `docs/methodology.md`). This is how v5 and v7 were evaluated.
- `evals/workflow.py` runs evaluated agents as Devin sessions. For another harness, give it the text from `evals/prompts.build_prompt(...)` and save the `final_message`, `patch` and `run_command` it returns to `evals/results/<run>/<label>.json`.
- Evaluated agents must not share memory or notes across sessions; see the isolation note in `docs/methodology.md`.
- `python3 evals/grade.py <run> [label filters]` replays the patches before and after the upstream fix. It expects the prepared checkouts under `~/grade/<case>/repo`, plus `fix.patch`, `upstream_test.patch` for urfave/cli, and `fix_grade.patch` for ripgrep-3009 and ts-60573 next to them.
- Per-case `SETUP` commands run after agent-patch application on the pre side and after agent/upstream-patch application on the post side, before each side's build and run command.
- Out-of-checkout prerequisites include the pydantic-11849 replay venv, pytest-13312's prepared host PyPy environment, and Go/Rust dependencies fetched during builds.

Patch files come from the case's upstream fix commit and `fix_prod_files` in `cases/cases.json`. `fix.patch` contains the fix's production-file changes; for `ALL_NON_TEST`, omit test files, testdata, docs, and changelog Markdown. `fix_grade.patch` is a grading-only production patch for ripgrep-3009 and ts-60573: it removes ripgrep's colliding upstream test functions and uses reduced context for TypeScript's CRLF checkout (see `docs/methodology.md`). `upstream_test.patch` contains urfave/cli's test and fixture changes from the fix commit; `POST_EXTRA` applies it after `fix.patch` so the updated tests compile against the changed API.

## Adding cases

Add an entry to `cases/cases.json` with the checkout, the fix commit and `fix_prod_files`. Then run `python3 evals/snapshot_issues.py <id>` (it needs `GH_TOKEN`) and check that the snapshot ends before maintainers diagnose the bug.
