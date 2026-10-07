"""Finish one run: record usage, collect, audit, grade (if the case has a fix), clean up.

usage: finish.py <plan-name> <run_id> <tokens> <tool_uses> <duration_ms>
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
TASKS = pathlib.Path("/tmp/claude-0/-home-user-recreate/a846bf6e-3413-543f-af03-2805ee54fa2e/tasks")
name, run_id, tokens, tools, ms = sys.argv[1:]
usage = pathlib.Path("/work/usage.json")
u = json.loads(usage.read_text()) if usage.exists() else {}
u[run_id] = {"tokens": int(tokens), "tool_uses": int(tools), "duration_ms": int(ms)}
usage.write_text(json.dumps(u, indent=1))
run = next(r for r in json.loads(pathlib.Path(f"/work/plan-{name}.json").read_text())["runs"] if r["run_id"] == run_id)
py = lambda *a: subprocess.run([sys.executable, *map(str, a)], check=True)
py(HERE / "harness.py", "collect", name, run_id)
agents = json.loads(pathlib.Path("/work/agents.json").read_text())
one = pathlib.Path(f"/work/agents-{run_id}.json")
one.write_text(json.dumps({run_id: agents[run_id]}))
py(HERE / "audit.py", one, TASKS, f"/work/plan-{name}.json")
case = {c["id"]: c for c in json.loads((HERE.parents[1] / "cases/cases.json").read_text())["cases"]}[run["case"]]
if case["fix"] and run["task"] == "reproduce":
    py(HERE / "grade_runs.py", f"sonnet-{name}", run_id)
py(HERE / "harness.py", "cleanup", run_id)
