"""Run evaluated agents as Devin child sessions.

Edit RUN below, then pass this file to run_workflow. Each agent's structured
output is written to evals/results/<RUN['name']>/<case>__<arm>__<task>.json.
When passing this file's text to run_workflow, run it from the repository root.
Repeated samples get numbered neutral prompt suffixes; duplicate session IDs
are recorded as errors instead of keeping a result.
Existing result-shaped labels outside the current work are rejected before
sessions start; metadata JSON files are ignored. Duplicate labels are rejected
before workflow registration.
"""
import asyncio, hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent if "__file__" in globals() else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT / "evals"))
from prompts import SCHEMA, build_prompt  # noqa: E402

RUN = {
    # Last run: the frozen skill on the holdout split. Earlier configs are recorded in evals/notes/.
    "name": "holdout-v3b",
    "arms": ["treatment"],
    # (split, case ids or None for every case in the split, tasks)
    "plan": [
        ("holdout", None, ["reproduce"]),
        ("holdout", ["eslint-19637", "pydantic-11849", "eslint-19033-fixed"], ["investigate"]),
        ("holdout", ["eslint-19957", "vue-13611"], ["fix"]),
    ],
}
# Skill text per arm; arms not listed get no skill.
SKILLS = {"treatment": "SKILL.md", "minimal": "evals/variants/SKILL-minimal.md"}


def units():
    cases = json.loads((ROOT / "cases/cases.json").read_text())["cases"]
    skills = {arm: (ROOT / path).read_text() for arm, path in SKILLS.items() if arm in RUN["arms"]}
    for split, ids, tasks in RUN["plan"]:
        if ids is not None:
            split_case_ids = {case["id"] for case in cases if case["split"] == split}
            missing = sorted(set(ids) - split_case_ids)
            if missing:
                raise ValueError(f"unknown case ids for split {split!r}: {', '.join(missing)}")
        for case in cases:
            if case["split"] != split or (ids is not None and case["id"] not in ids):
                continue
            report = (ROOT / "cases" / case["id"] / "issue.md").read_text()
            case = dict(case, report_date=re.search(r"Reported by @\S+ on (\S+)", report).group(1))
            for arm in RUN["arms"]:
                for task in tasks:
                    prompt = build_prompt(case, report, task, skills.get(arm))
                    label = f"{case['id']}__{arm}__{task}"
                    repeats = RUN.get("repeats", 1)
                    for n in range(1, repeats + 1):
                        sample_prompt = f"{prompt}\n\n(Evaluation sample {n}.)" if repeats > 1 else prompt
                        yield (f"{label}__r{n}" if repeats > 1 else label), sample_prompt


async def run_one(label, prompt, out_dir):
    try:
        result = await agent(prompt, phase="evaluate", schema=SCHEMA, label=label,
                             soft_time_limit_minutes=45)
    except WorkflowAgentError as e:
        result = {"error": str(e)}
    (out_dir / f"{label}.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    log(f"{label}: {'error' if 'error' in result else 'done'}")
    return result


def mark_duplicate_sessions(out_dir, labels):
    sessions_path = out_dir / "sessions.json"
    sessions = json.loads(sessions_path.read_text())
    by_session = {}
    for label in labels:
        session_id = sessions.get(label)
        if session_id is not None:
            by_session.setdefault(session_id, []).append(label)
    for session_id, duplicates in by_session.items():
        duplicates = sorted(set(duplicates))
        if len(duplicates) < 2:
            continue
        for label in duplicates[1:]:
            result_path = out_dir / f"{label}.json"
            result_path.write_text(json.dumps(
                {"error": f"duplicate session {session_id}"}, indent=2, sort_keys=True
            ))
            log(f"{label}: duplicate session {session_id}")


def result_json_labels(out_dir, case_ids):
    if not out_dir.exists():
        return set()
    labels = set()
    for path in out_dir.glob("*.json"):
        if not path.is_file():
            continue
        parts = path.stem.split("__")
        if len(parts) in (3, 4) and parts[0] in case_ids:
            labels.add(path.stem)
    return labels


def reject_stale_outputs(out_dir, work_labels, case_ids):
    stale = sorted(result_json_labels(out_dir, case_ids) - work_labels)
    if stale:
        raise ValueError(f"stale result labels in {out_dir}: {', '.join(stale)}")


def validate_prompt_manifest(out_dir, prompt_hashes, case_ids):
    manifest_path = out_dir / "prompts.json"
    result_labels = result_json_labels(out_dir, case_ids)
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        changed = sorted(
            label for label, prompt_hash in prompt_hashes.items()
            if label in previous and previous[label] != prompt_hash
        )
        if changed:
            raise ValueError(f"prompt hashes changed for labels: {', '.join(changed)}")
    elif result_labels:
        raise ValueError(
            f"legacy run directory {out_dir} has result JSONs but no prompts.json; use a new run name"
        )
    return manifest_path


def write_prompt_manifest(manifest_path, prompt_hashes):
    manifest_path.write_text(json.dumps(prompt_hashes, indent=2, sort_keys=True) + "\n")


def reject_duplicate_labels(work):
    counts = {}
    for label, _ in work:
        counts[label] = counts.get(label, 0) + 1
    duplicates = sorted(label for label, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate workflow labels: {', '.join(duplicates)}")
    return [label for label, _ in work]


async def main():
    work = list(units())
    labels = reject_duplicate_labels(work)
    out_dir = ROOT / "evals/results" / RUN["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    cases_path = ROOT / "cases/cases.json"
    case_ids = {case["id"] for case in json.loads(cases_path.read_text())["cases"]}
    prompt_hashes = {
        label: hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        for label, prompt in work
    }
    manifest_path = validate_prompt_manifest(out_dir, prompt_hashes, case_ids)
    reject_stale_outputs(out_dir, set(labels), case_ids)
    write_prompt_manifest(manifest_path, prompt_hashes)
    await register_workflow({
        "name": RUN["name"],
        "description": "Recreate eval: evaluated agents attempt bug reproduction from historical issues",
        "phases": [{"title": "evaluate", "detail": "one agent per case x arm x task",
                    "labels": labels}],
    })
    await asyncio.gather(*(run_one(label, prompt, out_dir) for label, prompt in work))
    mark_duplicate_sessions(out_dir, labels)


asyncio.run(main())
