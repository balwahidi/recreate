import json, pathlib, statistics as st, sys, re, collections
T = pathlib.Path("/tmp/claude-0/-home-user-recreate/a846bf6e-3413-543f-af03-2805ee54fa2e/tasks")
agents = json.loads(pathlib.Path("/work/agents.json").read_text())
runs = {}
for name in ["main", "confirm", "context"]:
    for r in json.loads(pathlib.Path(f"/work/plan-{name}.json").read_text())["runs"]:
        runs[r["run_id"]] = r
rows = []
cat_total = collections.Counter()
for rid, aid in agents.items():
    p = T / f"{aid}.output"
    if not p.exists() or rid not in runs: continue
    first = last = None; out_tok = 0
    chars = collections.Counter()
    biggest = []
    tool_names = {}
    for line in p.read_text(errors="replace").splitlines():
        try: rec = json.loads(line)
        except json.JSONDecodeError: continue
        msg = rec.get("message") or {}
        if not isinstance(msg, dict): continue
        u = msg.get("usage")
        if msg.get("role") == "assistant" and u:
            ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            if first is None: first = ctx
            last = ctx + u.get("output_tokens", 0); out_tok += u.get("output_tokens", 0)
        content = msg.get("content")
        if not isinstance(content, list): continue
        for b in content:
            if not isinstance(b, dict): continue
            t = b.get("type")
            if t == "tool_use":
                tool_names[b.get("id")] = b.get("name")
                chars["tool_input"] += len(json.dumps(b.get("input")))
            elif t == "tool_result":
                c = b.get("content")
                text = c if isinstance(c, str) else json.dumps(c)
                name = tool_names.get(b.get("tool_use_id"), "?")
                chars[f"result:{name}"] += len(text)
                biggest.append((len(text), name))
            elif t == "text":
                chars["assistant_text"] += len(b.get("text", ""))
            elif t == "thinking":
                chars["thinking"] += len(b.get("thinking", ""))
    r = runs[rid]
    rows.append(dict(rid=rid, arm=r["arm"], case=r["case"], task=r["task"], first=first, last=last, growth=last - first, out=out_tok, chars=chars, big=sorted(biggest, reverse=True)[:3]))
    cat_total.update(chars)
print("runs", len(rows))
print("baseline (first-turn context) median", st.median(x["first"] for x in rows), "min", min(x["first"] for x in rows), "max", max(x["first"] for x in rows))
print("final median", st.median(x["last"] for x in rows), "growth median", st.median(x["growth"] for x in rows))
for arm in ["none", "v3", "v5"]:
    s = [x for x in rows if x["arm"] == arm]
    print(f"{arm}: n={len(s)} baseline med {st.median(x['first'] for x in s):.0f}  growth med {st.median(x['growth'] for x in s):.0f}  output-tokens med {st.median(x['out'] for x in s):.0f}")
tot = sum(cat_total.values())
print("\nchars by category (all runs):")
for k, v in cat_total.most_common(12): print(f"  {k:<22} {v:>9}  {100*v/tot:5.1f}%")
print("\nlargest single tool results:")
allbig = sorted(((b[0], b[1], x["rid"], x["case"], x["arm"]) for x in rows for b in x["big"]), reverse=True)[:12]
for b in allbig: print("  ", b)
