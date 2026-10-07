"""Controller for the Sonnet evaluation (evaluated agents are Agent-tool subagents).

usage:
  harness.py plan <name>                 write /work/plan-<name>.json (frozen run list)
  harness.py provision <name> <run_id>   copy the case base into /work/runs/<run_id>, write the prompt
  harness.py collect <name> <run_id>     save final message, run command and patch to evals/results/<name>/
  harness.py cleanup <run_id>            delete the run's checkout (keeps out/)

Result labels are <case>__<run_id>__<task>: the arm is only in the plan file, so
grade logs can be adjudicated without knowing the arm.
"""
import hashlib, json, pathlib, random, re, secrets, shutil, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from cases import DEFAULT_ENV_NOTE, ENV_NOTE, WORKSPACE_SETUP  # noqa: E402
from prompts import SKILL_WRAPPER, TASKS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = pathlib.Path("/work")
SKILLS = {"v3": "evals/notes/SKILL-v3.md", "v5": "evals/variants/SKILL-v5.md", "v6": "evals/variants/SKILL-v6.md", "v7": "evals/variants/SKILL-v7.md", "none": None}

PROMPT = """You are working on the {repo} repository at a fixed revision. It is already checked out at {ws}/repo (commit {checkout}). {env_note}

Treat this checkout as the current main branch. Do not fetch newer commits of {repo}. Do not look up how this report was resolved: don't open this issue's page ({repo}#{issue}), any PR or commit that addresses it, or release notes published after {report_date}. Everything else is fine, including other issues, documentation, and installing published releases or any tooling you need.

This is an isolated evaluation task. Work only inside {ws}, plus /tmp for scratch files. Don't read, list or search anything else on this machine apart from system tools and package caches: nothing else under /home, /root or /work. Don't read or write persistent memory or notes, and don't save anything from this task to memory.

A user filed this bug report:

<report>
{report}
</report>

{task}

When you are done, reply to me as you normally would. Save that reply verbatim to {ws}/out/final_message.md. Save the command that demonstrates the bug, to be run from the repo root, to {ws}/out/run_command.txt (leave the file empty if you have none). Leave everything you want to keep in the working tree of {ws}/repo; it is collected as a patch. Then answer with only: DONE
"""

# Frozen experiment: (case, task, pairs). Arms within a pair run concurrently.
DESIGN = {
    "main": {
        "arms": ["v3", "v5"],
        "units": [
            ("eslint-19957", "reproduce", 2), ("eslint-19924", "reproduce", 2),
            ("eslint-19637", "reproduce", 2), ("vue-13611", "reproduce", 2),
            ("urfave-cli-2176", "reproduce", 2), ("pydantic-11849", "reproduce", 2),
            ("ripgrep-3009", "reproduce", 2), ("ts-60573", "reproduce", 2),
            ("eslint-20209-fixed", "reproduce", 2),
            ("eslint-19637", "investigate", 1), ("vue-13611", "investigate", 1),
        ],
    },
    "confirm": {
        "arms": ["v3", "v5"],
        "units": [("eslint-19924", "reproduce", 4), ("ts-60573", "reproduce", 4)],
    },
    "lean": {
        "arms": ["v5", "v6"],
        "units": [
            ("eslint-19957", "reproduce", 2), ("eslint-19924", "reproduce", 2),
            ("eslint-19637", "reproduce", 2), ("vue-13611", "reproduce", 2),
            ("urfave-cli-2176", "reproduce", 2), ("pydantic-11849", "reproduce", 2),
            ("ripgrep-3009", "reproduce", 2), ("ts-60573", "reproduce", 2),
            ("eslint-20209-fixed", "reproduce", 1),
            ("eslint-19637", "investigate", 1), ("vue-13611", "investigate", 1),
        ],
    },
    "short": {
        "arms": ["v5", "v7"],
        "units": [
            ("eslint-19957", "reproduce", 2), ("eslint-19924", "reproduce", 2),
            ("eslint-19637", "reproduce", 2), ("vue-13611", "reproduce", 2),
            ("urfave-cli-2176", "reproduce", 2), ("pydantic-11849", "reproduce", 2),
            ("ripgrep-3009", "reproduce", 2), ("ts-60573", "reproduce", 2),
            ("eslint-20209-fixed", "reproduce", 2),
            ("eslint-19637", "investigate", 1), ("vue-13611", "investigate", 1),
        ],
    },
    "context": {
        "arms": ["none"],
        "units": [
            ("eslint-19957", "reproduce", 1), ("eslint-19924", "reproduce", 1),
            ("eslint-19637", "reproduce", 1), ("vue-13611", "reproduce", 1),
            ("urfave-cli-2176", "reproduce", 1), ("pydantic-11849", "reproduce", 1),
            ("ripgrep-3009", "reproduce", 1), ("ts-60573", "reproduce", 1),
            ("eslint-20209-fixed", "reproduce", 1),
            ("eslint-19637", "investigate", 1), ("vue-13611", "investigate", 1),
        ],
    },
}


def registry():
    return {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}


def skill_text(arm):
    path = SKILLS[arm]
    return None if path is None else (ROOT / path).read_text()


def plan(name):
    out = WORK / f"plan-{name}.json"
    if out.exists():
        raise SystemExit(f"{out} exists; plans are frozen")
    seed = secrets.randbits(64)
    rng = random.Random(seed)
    runs, pair = [], 0
    for case, task, n in DESIGN[name]["units"]:
        for _ in range(n):
            pair += 1
            for arm in DESIGN[name]["arms"]:
                runs.append({"run_id": secrets.token_hex(5), "pair": pair, "case": case, "task": task, "arm": arm})
    pairs = sorted({r["pair"] for r in runs})
    rng.shuffle(pairs)  # launch order
    skills = {}
    for arm in DESIGN[name]["arms"]:
        text = skill_text(arm)
        skills[arm] = None if text is None else {
            "path": SKILLS[arm], "sha256": hashlib.sha256(text.encode()).hexdigest(), "words": len(text.split())}
    out.write_text(json.dumps({"name": name, "seed": seed, "launch_order": pairs, "skills": skills,
                               "model": "sonnet (Agent tool subagent)", "runs": runs}, indent=1) + "\n")
    print(out)


def load_plan(name):
    return json.loads((WORK / f"plan-{name}.json").read_text())


def find(name, run_id):
    return next(r for r in load_plan(name)["runs"] if r["run_id"] == run_id)


def provision(name, run_id):
    run = find(name, run_id)
    case = registry()[run["case"]]
    ws = WORK / "runs" / run_id
    if ws.exists():
        raise SystemExit(f"{ws} exists")
    (ws / "out").mkdir(parents=True)
    subprocess.run(["cp", "-a", "--reflink=auto", str(WORK / "base" / case["id"] / "repo"), str(ws / "repo")], check=True)
    if case["id"] in WORKSPACE_SETUP:
        subprocess.run(["bash", "-lc", WORKSPACE_SETUP[case["id"]]], cwd=ws / "repo", check=True)
    report = (ROOT / "cases" / case["id"] / "issue.md").read_text().strip()
    report_date = re.search(r"Reported by @\S+ on (\S+)", report).group(1)
    text = PROMPT.format(repo=case["repo"], ws=ws, checkout=case["checkout"], issue=case["issue"],
                         report_date=report_date, report=report, task=TASKS[run["task"]],
                         env_note=ENV_NOTE.get(case["id"], DEFAULT_ENV_NOTE))
    skill = skill_text(run["arm"])
    if skill is not None:
        text = SKILL_WRAPPER.format(skill=skill.strip()) + text
    (ws / "task.md").write_text(text)
    print(ws / "task.md")


def collect(name, run_id):
    run = find(name, run_id)
    case = registry()[run["case"]]
    ws = WORK / "runs" / run_id
    repo = ws / "repo"
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    patch = subprocess.run(["git", "diff", "--cached", "--binary", case["checkout"]], cwd=repo,
                           check=True, capture_output=True, text=True).stdout
    read = lambda p: p.read_text() if p.exists() else ""
    result = {
        "run_id": run_id,
        "final_message": read(ws / "out/final_message.md"),
        "run_command": read(ws / "out/run_command.txt").strip(),
        "patch": patch,
    }
    if not result["final_message"]:
        result["error"] = "no final message saved"
    out = ROOT / "evals/results" / f"sonnet-{name}"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{case['id']}__{run_id}__{run['task']}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{run_id}: message {len(result['final_message'])} chars, patch {len(patch)} chars, "
          f"run_command {'yes' if result['run_command'] else 'no'}")


def cleanup(run_id):
    shutil.rmtree(WORK / "runs" / run_id / "repo")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"plan": plan, "provision": provision, "collect": collect, "cleanup": cleanup}[cmd](*args)
