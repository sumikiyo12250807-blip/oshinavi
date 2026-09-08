# -*- coding: utf-8 -*-
"""統合4件を既存エントリへ足すための入力を作る（既存のぴあURLも一緒に渡す）。
🚨URLを2本以上渡さないと各ticketにurlが付かず、統合先の飛び先が消える
   （feedback_build_pia_multiurl_loses_ticket_url）。"""
import io, json, re, sys, collections
sys.stdout.reconfigure(encoding="utf-8")
MERGE = {7627: 6481, 7628: 6481, 7632: 2735, 7633: 2735}

mrg = json.load(io.open("tmp/built0101_merge_0909.json", encoding="utf-8"))
src = io.open("index.html", encoding="utf-8").read()
evs = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S).group(1))}

byid = collections.defaultdict(list)
for x in mrg:
    byid[MERGE[x["id"]]].append((x.get("links") or {}).get("pia"))

out = []
for eid, urls in byid.items():
    e = evs[eid]
    have = [(e.get("links") or {}).get("pia")]
    have += [t.get("url") for t in (e.get("tickets") or []) if t.get("url")]
    allurls = list(dict.fromkeys([u for u in have + urls if u and "pia" in u]))
    out.append({"newid": eid, "artist": e.get("artist") or e.get("name"), "urls": allurls})
    print("id%-6d %s ← URL %d本" % (eid, e.get("name", "")[:36], len(allurls)))
json.dump(out, io.open("tmp/merge2_input_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
