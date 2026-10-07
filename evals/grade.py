"""Replay agents' reproductions against the pre-fix and fixed revisions.

For each result with a run_command whose case has an upstream fix:
  1. reset ~/grade/<id>/repo to its checkout (tracked + untracked, ignored files kept)
  2. apply the agent's patch if present, run SETUP and BUILD, then run run_command -> "pre"
  3. reset the checkout, reapply the agent's patch if present, and apply the fix and
     any POST_EXTRA patch
  4. run SETUP and BUILD, then run run_command            -> "post"
A reproduction is fail-to-pass when pre exits non-zero (or times out) and post
exits zero. Flaky cases run each side RUNS_FLAKY times: pre must fail at least
once, post must never fail. pass_to_fail marks a command that exits zero before
the fix and non-zero after it (a bug detector with inverted exit status).
Output: evals/results/<run>/grade/<label>.json plus pre/post logs. Symptom
match is judged by hand from the logs.

usage: python3 evals/grade.py <run-name> [label-substring ...]
"""
import json, os, pathlib, signal, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRADE = pathlib.Path.home() / "grade"
RUNS_FLAKY = 3
TIMEOUT = {"default": 900, "ripgrep-3009": 300}
# Generated output the agents' commands consume; rebuilt on each side so "post" sees the fix.
BUILD = {
    "vite-20705": "pnpm --filter vite run build-bundle",
    "ts-60573": "npx hereby local",
    "pnpm-10290": "pnpm -C pnpm exec tsgo --build && pnpm -C pnpm run bundle",
}
SETUP = {
    "eslint-19245": "npm install --ignore-scripts",
    "eslint-19924": "npm install --ignore-scripts",
    "eslint-19818": "npm install --ignore-scripts",
    "eslint-18575-windows": "npm install --ignore-scripts",
    "eslint-20209-fixed": "npm install --ignore-scripts",
    "eslint-19957": "npm install --ignore-scripts",
    "eslint-19637": "npm install --ignore-scripts",
    "eslint-19033-fixed": "npm install --ignore-scripts",
    "vite-20705": "pnpm install --frozen-lockfile",
    "ts-60573": "npm ci --ignore-scripts",
    "pnpm-10290": "pnpm install --frozen-lockfile",
    "vue-12294": "{ [ -s ~/.nvm/nvm.sh ] && . ~/.nvm/nvm.sh; true; } && pnpm i --frozen-lockfile",
    "vue-13611": "{ [ -s ~/.nvm/nvm.sh ] && . ~/.nvm/nvm.sh; true; } && pnpm i --frozen-lockfile",
}
# Upstream fixes that change APIs existing tests use; their test changes are needed to compile.
POST_EXTRA = {"urfave-cli-2176": "upstream_test.patch"}


def sh(cmd, cwd, timeout):
    with tempfile.TemporaryFile(mode="w+b") as output:
        p = subprocess.Popen(
            ["bash", "-lc", cmd],
            cwd=cwd,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            code = "timeout"
        else:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = p.returncode
        output.seek(0)
        text = output.read().decode("utf-8", errors="replace")
        if len(text) > 40000:
            omitted = len(text) - 40000
            text = f"{text[:20000]}\n[... {omitted} chars truncated ...]\n{text[-20000:]}"
        return code, text


def reset(repo, checkout):
    subprocess.run(["git", "checkout", "-q", "-f", checkout], cwd=repo, check=True)
    subprocess.run(["git", "checkout", "-q", "--", "."], cwd=repo, check=True)
    subprocess.run(["git", "clean", "-ffdq"], cwd=repo, check=True)


def apply(repo, patch_text):
    if not patch_text or not patch_text.strip():
        return True, ""
    p = subprocess.run(["git", "apply", "--whitespace=nowarn", "-"], cwd=repo, input=patch_text,
                       capture_output=True, text=True)
    return p.returncode == 0, p.stderr[-2000:]


def side(repo, cmd, runs, timeout, log):
    codes = []
    with open(log, "w") as f:
        for i in range(runs):
            code, out = sh(cmd, repo, timeout)
            codes.append(code)
            f.write(f"===== run {i + 1}: exit {code}\n{out}\n")
    return codes


def build(case, repo, log):
    if case["id"] not in BUILD:
        return True
    code, out = sh(BUILD[case["id"]], repo, 1800)
    log.write_text(f"exit {code}\n{out}")
    return code == 0


def setup(case, repo, log):
    if case["id"] not in SETUP:
        return True
    code, out = sh(SETUP[case["id"]], repo, 1800)
    log.write_text(f"exit {code}\n{out}")
    return code == 0


def clear_grade_files(out_dir, label):
    (out_dir / f"{label}.json").unlink(missing_ok=True)
    for path in out_dir.glob(f"{label}.*.log"):
        path.unlink()


def purge_orphaned_grade_files(res_dir, out_dir, filters):
    if filters:
        return
    result_labels = {
        path.stem for path in res_dir.glob("*.json")
        if path.is_file() and len(path.stem.split("__")) in (3, 4)
    }
    orphan_labels = set()
    for path in out_dir.iterdir():
        if not path.is_file():
            continue
        label = path.name.split(".", 1)[0]
        if not label:
            continue
        is_grade_json = path.name == f"{label}.json"
        is_grade_log = path.name.startswith(f"{label}.") and path.name.endswith(".log")
        if (is_grade_json or is_grade_log) and label not in result_labels:
            orphan_labels.add(label)
    for label in sorted(orphan_labels):
        clear_grade_files(out_dir, label)


def grade(case, label, result, out_dir):
    repo = GRADE / case["id"] / "repo"
    runs = RUNS_FLAKY if "flaky" in case["kind"] else 1
    timeout = TIMEOUT.get(case["id"], TIMEOUT["default"])
    record = {"label": label, "case": case["id"], "runs_per_side": runs}
    try:
        reset(repo, case["checkout"])
        ok, err = apply(repo, result.get("patch") or "")
        if not ok:
            return dict(record, verdict="patch_failed", error=err)
        pre_setup_log = out_dir / f"{label}.pre.setup.log"
        if not setup(case, repo, pre_setup_log):
            return dict(record, verdict="setup_failed", side="pre", log=str(pre_setup_log))
        pre_build_log = out_dir / f"{label}.pre.build.log"
        if not build(case, repo, pre_build_log):
            return dict(record, verdict="build_failed", side="pre", log=str(pre_build_log))
        pre = side(repo, result["run_command"], runs, timeout, out_dir / f"{label}.pre.log")
        reset(repo, case["checkout"])
        ok, err = apply(repo, result.get("patch") or "")
        if not ok:
            return dict(record, verdict="patch_failed", error=err, pre=pre)
        # fix_grade.patch: the fix without upstream test hunks that collide with agents' tests
        fix = "fix_grade.patch" if (GRADE / case["id"] / "fix_grade.patch").exists() else "fix.patch"
        for name in [fix] + ([POST_EXTRA[case["id"]]] if case["id"] in POST_EXTRA else []):
            ok, err = apply(repo, (GRADE / case["id"] / name).read_text())
            if not ok:
                return dict(record, verdict="fix_conflicts_with_patch", error=f"{name}: {err}", pre=pre)
        post_setup_log = out_dir / f"{label}.post.setup.log"
        if not setup(case, repo, post_setup_log):
            return dict(record, verdict="setup_failed", side="post", log=str(post_setup_log), pre=pre)
        post_build_log = out_dir / f"{label}.post.build.log"
        if not build(case, repo, post_build_log):
            return dict(record, verdict="build_failed", side="post", log=str(post_build_log))
        post = side(repo, result["run_command"], runs, timeout, out_dir / f"{label}.post.log")
    finally:
        reset(repo, case["checkout"])
    return dict(record, verdict=classify(pre, post), pre=pre, post=post)


def classify(pre, post):
    """pass_to_fail is an inverted harness: it exits 0 while the bug is present."""
    pre_failed = any(c != 0 for c in pre)
    post_failed = any(c != 0 for c in post)
    if pre_failed:
        return "fails_both" if post_failed else "fail_to_pass"
    return "pass_to_fail" if post_failed else "passes_pre"


def main():
    run, filters = sys.argv[1], sys.argv[2:]
    cases = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}
    res_dir = ROOT / "evals/results" / run
    out_dir = res_dir / "grade"
    out_dir.mkdir(exist_ok=True)
    purge_orphaned_grade_files(res_dir, out_dir, filters)
    for path in sorted(res_dir.glob("*.json")):
        label = path.stem
        if label.split("__")[0] not in cases or (filters and not any(f in label for f in filters)):
            continue
        clear_grade_files(out_dir, label)
        case = cases[label.split("__")[0]]
        result = json.loads(path.read_text())
        has_error = "error" in result
        no_artifact = not result.get("run_command")
        if has_error:
            record = {"label": label, "case": case["id"], "verdict": "agent_error"}
        elif not case["fix"]:
            continue
        elif no_artifact:
            record = {"label": label, "case": case["id"], "verdict": "no_reproduction_artifact"}
        else:
            record = grade(case, label, result, out_dir)
        (out_dir / f"{label}.json").write_text(json.dumps(record, indent=2))
        print(f"{label}: {record['verdict']} pre={record.get('pre')} post={record.get('post')}", flush=True)


if __name__ == "__main__":
    main()
