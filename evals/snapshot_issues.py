"""Write cases/<id>/issue.md: the issue as the agent may see it.

Comments at or after the case's cutoff are withheld so the agent cannot read
the maintainers' diagnosis or the fix. Cutoff tokens in cases.json:
  FIX_PR_CREATED              creation time of the PR that merged `fix`
  FIRST_NON_REPORTER_COMMENT  first comment by anyone other than the reporter
  <ISO timestamp>             literal
Requires an authenticated `gh` CLI.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ONLY = set(sys.argv[1:])


def gh(path):
    out = subprocess.run(["gh", "api", "--paginate", path], check=True, capture_output=True, text=True).stdout
    # --paginate concatenates JSON arrays as "][": normalise.
    return json.loads(out.replace("]\n[", ",").replace("][", ","))


def cutoff(case, issue, comments):
    token = case["snapshot_before"]
    if token == "FIX_PR_CREATED":
        prs = gh(f"repos/{case['repo']}/commits/{case['fix']}/pulls")
        return min(p["created_at"] for p in prs)
    if token == "FIRST_NON_REPORTER_COMMENT":
        others = [c["created_at"] for c in comments if c["user"]["login"] != issue["user"]["login"]]
        return min(others) if others else "9999"
    return token


def main():
    cases = json.loads((ROOT / "cases/cases.json").read_text())["cases"]
    for case in cases:
        if ONLY and case["id"] not in ONLY:
            continue
        issue = gh(f"repos/{case['repo']}/issues/{case['issue']}")
        comments = gh(f"repos/{case['repo']}/issues/{case['issue']}/comments")
        limit = cutoff(case, issue, comments)
        kept = [c for c in comments if c["created_at"] < limit]
        parts = [f"# {issue['title']}\n",
                 f"Reported by @{issue['user']['login']} on {issue['created_at'][:10]}\n",
                 issue["body"] or ""]
        for c in kept:
            parts.append(f"\n---\n\n**@{c['user']['login']}** commented on {c['created_at'][:10]}:\n\n{c['body']}")
        out = ROOT / "cases" / case["id"] / "issue.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(parts).rstrip() + "\n")
        print(f"{case['id']}: cutoff={limit} kept {len(kept)}/{len(comments)} comments")


if __name__ == "__main__":
    main()
