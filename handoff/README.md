The Recreate handoff for Claude Code is ready in [HANDOFF.md](HANDOFF.md). It contains the current project state, user constraints, two completed experiments, exact measurements, limitations and proposed next work.

This folder was first published on branch `codex/claude-handoff-2026-10-07` and is now archived on `main`. Download the [evidence archive](recreate-claude-handoff.tar.gz) using GitHub’s raw/download button, or clone the repository:

```sh
git clone https://github.com/balwahidi/recreate.git
cd recreate/handoff
sha256sum -c recreate-claude-handoff.sha256
tar -xzf recreate-claude-handoff.tar.gz
```

Give Claude Code this instruction:

> Read handoff/HANDOFF.md first and review the evidence under handoff/recreate-claude-handoff/. Audit the completed experiments, preserve existing work, and propose the next controlled experiment. Do not change SKILL.md without measured improvement. Keep evaluator evidence and upstream fixes out of evaluated agents’ contexts.

The archive contains the exact tested 291-word skill, the pre-existing local README/SKILL patch, frozen prompts and protocols, agent artifacts, command traces, upstream replay logs and a SHA-256 manifest. The tested working copy had local edits, so the repository-root SKILL.md on this branch is not a substitute for the archived tested snapshot. Inspect the snapshot and patch before continuing development.

The latest experiment attempted twelve GPT-6.1 Sol/medium contexts: eleven completed and one was stopped by a platform risk filter. The proposed skill sentence did not earn adoption. No skill improvement was installed. Full results and the distinction between faithful evidence and the grader’s exit-code convention are documented in the handoff.

This is portable audit evidence. Dependencies, complete target checkouts and build tools are excluded; replay helpers contain original cloud paths and require adaptation on another machine. No experiment is currently running. The handoff package doesn't alter the root skill or README. Its audit is [`evals/notes/audit-2026-10-07.md`](../evals/notes/audit-2026-10-07.md).
