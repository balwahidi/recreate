"""Grade "Fix this bug." runs against upstream's own tests, which the agent never saw.

usage: grade_fix.py <results-dir-name> [label-substring ...]
       grade_fix.py --validate <case>   check the instrument: fails at the checkout, passes with the upstream fix

For each run: reset ~/grade/<case>/repo to the checkout, apply the agent's whole patch, put the
upstream fix's test changes on top (overwriting the agent's edits to those files), restore the
neighbouring test files to the checkout, and run the case's command. F (fixed) = the patch applies
and every run of the command exits 0. Only upstream's tests and tests that existed at the checkout
run, never the agent's own: a correct fix shouldn't fail because of a test its author added.
"""
import json, pathlib, re, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import grade  # noqa: E402  (reset, apply, sh)

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRADE = grade.GRADE
TS_TESTS = [
    "tests/baselines/reference/declarationAssertionNodeNotReusedWhenTypeNotEquivalent1.js",
    "tests/baselines/reference/declarationAssertionNodeNotReusedWhenTypeNotEquivalent1.symbols",
    "tests/baselines/reference/declarationAssertionNodeNotReusedWhenTypeNotEquivalent1.types",
    "tests/cases/compiler/declarationAssertionNodeNotReusedWhenTypeNotEquivalent1.ts",
    "tests/cases/fourslash/quickInfoAssertionNodeNotReusedWhenTypeNotEquivalent1.ts",
]
HIDDEN = {
    "eslint-19957": {
        "files": ["tests/lib/rules/no-loss-of-precision.js"],
        "cmd": "npx mocha --timeout 60000 tests/lib/rules/no-loss-of-precision.js",
    },
    "eslint-19637": {
        "files": ["tests/lib/rules/no-unused-expressions.js"],
        "base_files": ["tests/lib/rules/utils/ast-utils.js"],
        "cmd": "npx mocha --timeout 60000 tests/lib/rules/no-unused-expressions.js tests/lib/rules/utils/ast-utils.js",
    },
    "eslint-19924": {
        "files": ["tools/check-emfile-handling.js", "tests/fixtures/emfile/eslint.config.js"],
        "base_files": ["tests/lib/eslint/eslint.js"],
        "cmd": "ulimit -n 1024 && node tools/check-emfile-handling.js && npx mocha --timeout 60000 tests/lib/eslint/eslint.js",
    },
    "vue-13611": {
        "files": ["packages/runtime-core/__tests__/componentSlots.spec.ts"],
        "base_files": ["packages/compiler-core/__tests__/transforms/vSlot.spec.ts"],
        "cmd": "pnpm vitest run packages/runtime-core/__tests__/componentSlots.spec.ts "
               "packages/compiler-core/__tests__/transforms/vSlot.spec.ts",
    },
    "ripgrep-3009": {
        "rust_tests": "crates/ignore/src/walk.rs",
        # The lib tests that existed at the checkout, plus the two hidden ones, by exact name.
        "cmd": "cargo test --offline -q -p ignore --lib -- --exact $(cat {here}/ripgrep-3009-base-tests.txt) "
               "walk::tests::hidden_panic_in_parallel walk::tests::hidden_panic_in_parallel_builder",
        "runs": 3,
        "timeout": 300,
    },
    "ts-60573": {
        "files": TS_TESTS,
        "base_dirs": ["tests/cases", "tests/baselines/reference"],
        # The new test, then declaration-emit neighbours that a too-broad change to node reuse would break.
        "cmd": "npx hereby runtests --tests=AssertionNodeNotReusedWhenTypeNotEquivalent1 && "
               "npx hereby runtests --tests=declarationEmit && npx hereby runtests --tests=isolatedDeclaration",
    },
}
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)(/|$)|[._-](test|spec)\.[a-z]+$|_test\.go$")


def upstream_rust_tests(repo, fix, path):
    """The test functions the fix adds to an inline `mod tests`, renamed so they can't collide."""
    diff = subprocess.run(["git", "show", fix, "--", path], cwd=repo, capture_output=True, text=True, check=True).stdout
    hunk = diff[diff.rindex("@@ "):]
    added = [l[1:] for l in hunk.splitlines()[1:] if l.startswith("+")]
    return re.sub(r"\bfn (\w+)\(", r"fn hidden_\1(", "\n".join(added))


def install_tests(case, repo, spec):
    for d in spec.get("base_dirs", []):
        subprocess.run(["git", "checkout", case["checkout"], "--", d], cwd=repo, check=True)
        subprocess.run(["git", "clean", "-fdq", "--", d], cwd=repo, check=True)
    if spec.get("base_files"):
        subprocess.run(["git", "checkout", case["checkout"], "--", *spec["base_files"]], cwd=repo, check=True)
    if "files" in spec:
        subprocess.run(["git", "checkout", case["fix"], "--", *spec["files"]], cwd=repo, check=True)
    if "rust_tests" in spec:
        f = repo / spec["rust_tests"]
        src = f.read_text()
        end = src.rstrip().rindex("}")  # the inline `mod tests` closes the file
        f.write_text(src[:end] + upstream_rust_tests(repo, case["fix"], spec["rust_tests"]) + "\n" + src[end:])


def drop_overwritten(patch, spec):
    """Leave out the agent's changes to files install_tests replaces anyway, so they can't block the apply."""
    exact = set(spec.get("files", [])) | set(spec.get("base_files", []))
    dirs = tuple(d.rstrip("/") + "/" for d in spec.get("base_dirs", []))
    keep = []
    for chunk in re.split(r"(?m)^(?=diff --git )", patch or ""):
        m = re.match(r"diff --git a/(\S+)", chunk)
        if m and (m.group(1) in exact or m.group(1).startswith(dirs)):
            continue
        keep.append(chunk)
    return "".join(keep)


def run_hidden(case, patch, log):
    spec = HIDDEN[case["id"]]
    repo = GRADE / case["id"] / "repo"
    grade.reset(repo, case["checkout"])
    ok, err = grade.apply(repo, drop_overwritten(patch, spec))
    if not ok:
        log.write_text(f"agent patch does not apply:\n{err}")
        grade.reset(repo, case["checkout"])
        return {"F": False, "applied": False, "codes": []}
    install_tests(case, repo, spec)
    # A private TMPDIR: ESLint's tests copy fixtures to $TMPDIR/eslint, which agents running alongside also use.
    cmd = "export TMPDIR=$(mktemp -d) && " + spec["cmd"].replace("{here}", str(pathlib.Path(__file__).resolve().parent))
    codes = grade.side(repo, cmd, spec.get("runs", 1), spec.get("timeout", 1800), log)
    grade.reset(repo, case["checkout"])
    return {"F": all(c == 0 for c in codes), "applied": True, "codes": codes}


def patch_facts(patch):
    files = re.findall(r"(?m)^diff --git a/(\S+)", patch or "")
    added = "\n".join(l for l in (patch or "").splitlines() if l.startswith("+"))
    return {
        "files": files,
        "test_in_patch": any(TEST_PATH.search(f) for f in files) or "#[test]" in added,
    }


def validate(cid):
    case = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}[cid]
    out = ROOT / "evals/results/fix-validate"
    out.mkdir(parents=True, exist_ok=True)
    fix_name = "fix_grade.patch" if (GRADE / cid / "fix_grade.patch").exists() else "fix.patch"
    fix = (GRADE / cid / fix_name).read_bytes().decode()
    base = run_hidden(case, "", out / f"{cid}.base.log")
    fixed = [run_hidden(case, fix, out / f"{cid}.fix{i}.log") for i in range(2)]
    verdict = "ok" if not base["F"] and all(f["F"] for f in fixed) else "INVALID"
    print(f"{cid}: base {base['codes']} upstream-fix {[f['codes'] for f in fixed]} -> {verdict}", flush=True)


def main():
    run, filters = sys.argv[1], sys.argv[2:]
    cases = {c["id"]: c for c in json.loads((ROOT / "cases/cases.json").read_text())["cases"]}
    res_dir = ROOT / "evals/results" / run
    out_dir = res_dir / "grade"
    out_dir.mkdir(exist_ok=True)
    for path in sorted(res_dir.glob("*__fix.json")):
        label = path.stem
        if filters and not any(f in label for f in filters):
            continue
        case = cases[label.split("__")[0]]
        result = json.loads(path.read_text())
        record = {"label": label, "case": case["id"], **patch_facts(result.get("patch"))}
        if "error" in result:
            record.update(F=False, error=result["error"])
        else:
            record.update(run_hidden(case, result.get("patch", ""), out_dir / f"{label}.log"))
        (out_dir / f"{label}.json").write_text(json.dumps(record, indent=2))
        print(f"{label}: F={record['F']} codes={record.get('codes')} test_in_patch={record['test_in_patch']}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--validate":
        validate(sys.argv[2])
    else:
        main()
