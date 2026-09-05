# -*- coding: utf-8 -*-
"""当て込む前に「url が無い枠を足してよいエントリか」を判定する。

🚨 url が空の枠は、そのエントリの links（rakuten>pia>eplus…）に飛ぶ。
   **ぴあURLが1本しか無いエントリ**なら、その1本＝links.pia なので飛び先は正しい。
   **2本以上あるエントリ**だと、別会場のページに着地する
   （[[feedback_build_pia_multiurl_loses_ticket_url]]／[[feedback_tour_per_ticket_url]]）。

出力: tmp/check_urlneed_0905.txt
"""
import re, json, io, sys

BUILT = sys.argv[1] if len(sys.argv) > 1 else "tmp/zeroA_built_0905.json"

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}


def pia_cds(e):
    cds = set()
    u = (e.get("links") or {}).get("pia") or ""
    mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
    if mm:
        cds.add(mm.group(1))
    for t in e.get("tickets") or []:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", t.get("url") or "")
        if mm:
            cds.add(mm.group(1))
    return cds


ok, ng, buf = [], [], []
for b in json.load(io.open(BUILT, encoding="utf-8")):
    e = by.get(b["id"])
    if not e:
        continue
    nourl = [t for t in (b.get("tickets") or []) if not (t.get("url") or "").strip()]
    if not nourl:
        continue
    cds = pia_cds(e)
    if len(cds) <= 1:
        ok.append(b["id"])
        buf.append("OK   id=%-5s %s  ぴあURL%d本 → url無し%d枠は links.pia に飛べば正しい"
                   % (b["id"], e.get("name", "")[:34], len(cds), len(nourl)))
    else:
        ng.append(b["id"])
        buf.append("🚨NG id=%-5s %s  ぴあURL%d本あるのに url無し%d枠 → 別会場に着地する"
                   % (b["id"], e.get("name", "")[:34], len(cds), len(nourl)))
        for t in nourl:
            buf.append("        %s" % t.get("type"))
        buf.append("        ぴあURL: %s" % ", ".join(sorted(cds)))

buf.append("")
buf.append("足してよい: %d件 / 危ない: %d件 %s" % (len(ok), len(ng), ng))
io.open("tmp/check_urlneed_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("SAFE=%d RISKY=%d %s" % (len(ok), len(ng), ng))
