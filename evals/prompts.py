"""Prompts given to evaluated agents. Both arms receive identical text except
that the treatment arm also receives SKILL.md as an installed skill."""

SETUP = """You are working on the {repo} repository at a fixed revision. Set it up with:

    git init repo && cd repo
    git fetch --depth=500 https://github.com/{repo}.git {checkout}
    git checkout FETCH_HEAD

Treat this checkout as the current main branch. Do not fetch newer commits of {repo}. Do not look up how this report was resolved: don't open this issue's page ({repo}#{issue}), any PR or commit that addresses it, or release notes published after {report_date}. Everything else is fine, including other issues, documentation, and installing published releases or any tooling you need.

This is an isolated evaluation task. Don't read or write your persistent memory or notes (e.g. ~/memory), and don't save anything from this task to memory.

A user filed this bug report:

<report>
{report}
</report>
"""

TASKS = {
    "reproduce": "Reproduce this bug. Don't fix it; I want a reproduction to investigate the cause from.",
    "investigate": "Look into this bug report.",
    "fix": "Fix this bug.",
}

SKILL_WRAPPER = """The following agent skill is installed. Use it when it applies.

<skill name="recreate">
{skill}
</skill>

"""

OUTPUT = """
When you are done, reply to me as you normally would, then provide structured output:
- final_message: your reply to me, verbatim.
- patch: output of `git add -A && git diff --cached --binary` in the repo (everything you left in the working tree), or "" if nothing.
- run_command: if you have a command that demonstrates the bug, the command to run from the repo root after applying the patch; otherwise "".
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "final_message": {"type": "string"},
        "patch": {"type": "string"},
        "run_command": {"type": "string"},
    },
    "required": ["final_message", "patch", "run_command"],
}


def build_prompt(case, report, task, skill=None):
    text = SETUP.format(repo=case["repo"], checkout=case["checkout"], issue=case["issue"],
                        report_date=case["report_date"], report=report.strip())
    text += "\n" + TASKS[task] + "\n" + OUTPUT
    if skill is not None:
        text = SKILL_WRAPPER.format(skill=skill.strip()) + text
    return text
