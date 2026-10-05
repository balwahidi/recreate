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
    out = subprocess.run(
        ["gh", "api", "--paginate", "--slurp", path],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    pages = json.loads(out)
    if not isinstance(pages, list):
        raise ValueError(f"expected --slurp to return a list of pages for {path}")
    if all(isinstance(page, list) for page in pages):
        return [item for page in pages for item in page]
    if len(pages) == 1 and isinstance(pages[0], dict):
        return pages[0]
    raise ValueError(f"unexpected --slurp page structure for {path}")


def cutoff(case, issue, comments):
    token = case["snapshot_before"]
    if token == "FIX_PR_CREATED":
        prs = gh(f"repos/{case['repo']}/commits/{case['fix']}/pulls")
        return min(p["created_at"] for p in prs)
    if token == "FIRST_NON_REPORTER_COMMENT":
        others = [c["created_at"] for c in comments if c["user"]["login"] != issue["user"]["login"]]
        return min(others) if others else "9999"
    return token


def body_at_cutoff(case, issue, limit):
    owner, name = case["repo"].split("/")
    query = """
    query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        issue(number: $number) {
          userContentEdits(first: 100, after: $cursor) {
            nodes { editedAt diff }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }
    """
    nodes = []
    cursor = None
    while True:
        args = [
            "gh", "api", "graphql", "-f", f"query={query}",
            "-F", f"owner={owner}", "-F", f"name={name}",
            "-F", f"number={case['issue']}",
        ]
        if cursor:
            args.extend(["-F", f"cursor={cursor}"])
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        connection = json.loads(result.stdout)["data"]["repository"]["issue"]["userContentEdits"]
        nodes.extend(connection["nodes"])
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    if not nodes:
        return issue["body"] or ""

    nodes.sort(key=lambda node: node["editedAt"])
    current = issue["body"] or ""
    if nodes[-1]["diff"] != current:
        raise ValueError(f"latest GraphQL body edit does not match current body for {case['id']}")

    eligible = [node for node in nodes if node["editedAt"] < limit]
    if eligible:
        return eligible[-1]["diff"]
    if nodes[0]["editedAt"] != issue["created_at"]:
        raise ValueError(f"GraphQL history does not expose the original body for {case['id']}")
    return nodes[0]["diff"]


def main():
    cases = json.loads((ROOT / "cases/cases.json").read_text())["cases"]
    outputs = []
    for case in cases:
        if ONLY and case["id"] not in ONLY:
            continue
        issue = gh(f"repos/{case['repo']}/issues/{case['issue']}")
        comments = gh(f"repos/{case['repo']}/issues/{case['issue']}/comments")
        limit = cutoff(case, issue, comments)
        kept = [c for c in comments if c["created_at"] < limit]
        parts = [f"# {issue['title']}\n",
                 f"Reported by @{issue['user']['login']} on {issue['created_at'][:10]}\n",
                 body_at_cutoff(case, issue, limit)]
        for c in kept:
            parts.append(f"\n---\n\n**@{c['user']['login']}** commented on {c['created_at'][:10]}:\n\n{c['body']}")
        out = ROOT / "cases" / case["id"] / "issue.md"
        outputs.append((case["id"], out, "\n".join(parts).rstrip() + "\n", limit, len(kept), len(comments)))

    for case_id, out, text, limit, kept, total in outputs:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"{case_id}: cutoff={limit} kept {kept}/{total} comments")


if __name__ == "__main__":
    main()
