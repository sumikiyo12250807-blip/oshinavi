# -*- coding: utf-8 -*-
"""9/8 発売前スイープの未掲載候補150件を投入候補にする。

🚨 newid は「これまでに使った最大id」+1（現物の最大id+1 だと削除済みidを再利用してしまう）。
🚨 URLは t.pia.jp の正規形に直す（スイープの出力は ticket.pia.jp 形）。
🚨 同じ eventCd は1件にまとめる。
"""
import io, re, json

cand_src = json.load(io.open("tmp/sweep_cand_0908.json", encoding="utf-8"))

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
st = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
nid = max([max(e["id"] for e in EV)] + [b.get("id_to", 0) for b in st["batches"]]) + 1

def canon(u):
    m = re.search(r"eventBundleCd=([\w]+)", u or "")
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventBundleCd=%s" % m.group(1)
    m = re.search(r"eventCd=([\w]+)", u or "")
    if m:
        return "https://t.pia.jp/pia/event/event.do?eventCd=%s" % m.group(1)
    return u

seen, cand = set(), []
for c in cand_src:
    u = canon(c.get("url"))
    key = re.sub(r".*=", "", u)
    if not key or key in seen:
        continue
    seen.add(key)
    cand.append({"newid": nid, "artist": (c.get("artist") or "").strip(), "urls": [u],
                 "_pref": c.get("pref", ""), "_perf": c.get("perfdate", ""),
                 "_rls": c.get("rlsdate", ""), "_lg": c.get("_lg", ""),
                 "_name_in_db": bool(c.get("name_in_db"))})
    nid += 1

json.dump([{k: v for k, v in c.items() if not k.startswith("_")} for c in cand],
          io.open("tmp/cand_0908.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

with io.open("tmp/cand_0908.txt", "w", encoding="utf-8") as f:
    f.write("=== 投入候補 %d件（id %s..%s）===\n" % (len(cand), cand[0]["newid"], cand[-1]["newid"]))
    f.write("うち 同名の既存あり＝%d件（投入前に1件ずつ確かめる）\n\n"
            % sum(1 for c in cand if c["_name_in_db"]))
    for c in cand:
        f.write("  id=%-6s %-40s 発売%-11s 公演%-24s %s%s\n"
                % (c["newid"], c["artist"][:40], c["_rls"], c["_perf"][:24], c["_pref"],
                   "  ※同名あり" if c["_name_in_db"] else ""))
print("候補 %d件 → tmp/cand_0908.json (id %s..%s)" % (len(cand), cand[0]["newid"], cand[-1]["newid"]))
