"""Prepare agent bases (/work/base/<case>/repo) and grading checkouts (~/grade/<case>).

The agent base fetches only the pinned checkout. The grading checkout is a copy that
also fetches the fix commit, writes fix.patch (production files only), and checks it
applies. usage: python3 evals/sonnet/prepare.py <case> [...]
"""
import json, pathlib, shutil, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from cases import AGENT_SETUP

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = pathlib.Path("/work/base")
GRADE = pathlib.Path.home() / "grade"
TEST_HINTS = ("test", "testdata", "fixtures", "__tests__", "docs/", "CHANGELOG", ".md")


def sh(cmd, cwd, log=None):
    print(f"[{cwd}] $ {cmd}", flush=True)
    out = subprocess.run(["bash", "-lc", cmd], cwd=cwd, capture_output=True, text=True)
    if log:
        log.write_text(out.stdout + out.stderr)
    if out.returncode:
        print(out.stdout[-3000:], out.stderr[-3000:], flush=True)
        raise SystemExit(f"failed ({out.returncode}): {cmd}")
    return out.stdout


def prod_files(case, repo):
    files = case["fix_prod_files"]
    if files != "ALL_NON_TEST":
        return files
    changed = sh(f"git diff --name-only {case['fix']}^ {case['fix']}", repo).split()
    return [f for f in changed if not any(h in f for h in TEST_HINTS) and not f.endswith("_test.go")]


def prepare(case):
    cid = case["id"]
    base = BASE / cid
    repo = base / "repo"
    if not (base / "READY").exists():
        shutil.rmtree(base, ignore_errors=True)
        base.mkdir(parents=True)
        sh("git init -q repo", base)
        sh(f"git fetch -q --depth=500 https://github.com/{case['repo']}.git {case['checkout']} && git checkout -q FETCH_HEAD", repo)
        sh(AGENT_SETUP[cid], repo, base / "setup.log")
        (base / "READY").write_text("ok\n")
    if not case["fix"]:
        return
    g = GRADE / cid
    if (g / "READY").exists():
        return
    shutil.rmtree(g, ignore_errors=True)
    g.mkdir(parents=True)
    sh(f"cp -a --reflink=auto {repo} {g}/repo", g)
    grepo = g / "repo"
    sh(f"git fetch -q --depth=2 https://github.com/{case['repo']}.git {case['fix']}", grepo)
    files = prod_files(case, grepo)
    (g / "fix_files.json").write_text(json.dumps(files, indent=1))
    patch = sh(f"git diff --binary {case['fix']}^ {case['fix']} -- " + " ".join(files), grepo)
    (g / "fix.patch").write_text(patch)
    sh(f"git apply --check {g}/fix.patch", grepo)
    (g / "READY").write_text("ok\n")


if __name__ == "__main__":
    cases = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}
    for cid in sys.argv[1:]:
        prepare(cases[cid])
        print(f"== {cid} ready", flush=True)
