"""Write cases/<id>/issue.md: the issue as the agent may see it.

Issue titles and bodies are restored to the case's cutoff. Comments at or
after the cutoff are withheld so the agent cannot read the diagnosis or fix.
Cutoff tokens in cases.json:
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


def title_at_cutoff(case, issue, events, limit):
    renames = sorted(
        (event for event in events if event.get("event") == "renamed"),
        key=lambda event: event["created_at"],
    )
    title = issue["title"]
    if renames and renames[-1]["rename"]["to"] != title:
        raise ValueError(f"latest issue rename does not match current title for {case['id']}")
    for event in reversed(renames):
        if event["created_at"] >= limit:
            title = event["rename"]["from"]
    return title


def content_at_cutoff(nodes, current_body, created_at, limit):
    current = current_body or ""
    if not nodes:
        return current
    nodes = sorted(nodes, key=lambda node: node["editedAt"])
    if nodes[-1]["diff"] != current:
        raise ValueError("latest GraphQL body edit does not match current body")
    eligible = [node for node in nodes if node["editedAt"] < limit]
    if eligible:
        return eligible[-1]["diff"]
    if nodes[0]["editedAt"] != created_at:
        raise ValueError("GraphQL history does not expose the original body")
    return nodes[0]["diff"]


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

    return content_at_cutoff(nodes, issue["body"], issue["created_at"], limit)


def comment_body_at_cutoff(comment, limit):
    query = """
    query($id: ID!, $cursor: String) {
      node(id: $id) {
        ... on IssueComment {
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
        args = ["gh", "api", "graphql", "-f", f"query={query}", "-F", f"id={comment['node_id']}"]
        if cursor:
            args.extend(["-F", f"cursor={cursor}"])
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        node = json.loads(result.stdout)["data"]["node"]
        if node is None:
            raise ValueError(f"GraphQL comment not found: {comment['node_id']}")
        connection = node.get("userContentEdits") or {}
        nodes.extend(connection.get("nodes") or [])
        page = connection.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            break
        cursor = page["endCursor"]
    return content_at_cutoff(nodes, comment["body"], comment["created_at"], limit)


def main():
    cases = json.loads((ROOT / "cases/cases.json").read_text())["cases"]
    outputs = []
    for case in cases:
        if ONLY and case["id"] not in ONLY:
            continue
        issue = gh(f"repos/{case['repo']}/issues/{case['issue']}")
        comments = gh(f"repos/{case['repo']}/issues/{case['issue']}/comments")
        events = gh(f"repos/{case['repo']}/issues/{case['issue']}/events")
        limit = cutoff(case, issue, comments)
        title = title_at_cutoff(case, issue, events, limit)
        kept = [c for c in comments if c["created_at"] < limit]
        parts = [f"# {title}\n",
                 f"Reported by @{issue['user']['login']} on {issue['created_at'][:10]}\n",
                 body_at_cutoff(case, issue, limit)]
        for c in kept:
            body = comment_body_at_cutoff(c, limit)
            parts.append(f"\n---\n\n**@{c['user']['login']}** commented on {c['created_at'][:10]}:\n\n{body}")
        out = ROOT / "cases" / case["id"] / "issue.md"
        outputs.append((case["id"], out, "\n".join(parts).rstrip() + "\n", limit, len(kept), len(comments)))

    for case_id, out, text, limit, kept, total in outputs:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"{case_id}: cutoff={limit} kept {kept}/{total} comments")


if __name__ == "__main__":
    main()
