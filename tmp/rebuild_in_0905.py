# -*- coding: utf-8 -*-
"""指定した既存エントリを、そのエントリの**ぴあURL全部**から再ビルドするための入力を作る。

🚨 URLは1本だけ渡すと multi=False になって ticket.url が刻まれない
   （[[feedback_build_pia_multiurl_loses_ticket_url]]）。必ず全部渡す。
🚨 これは「取り直し」用。当て込みは merge_apply（追加と補完だけ）で行い、置換しない。

使い方: python tmp/rebuild_in_0905.py <出力.json> <id> <id> ...
"""
import re, json, io, sys

OUT = sys.argv[1]
ids = [int(a) for a in sys.argv[2:]]

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}


def pia_urls(e):
    out, seen, uniq = [], set(), []
    u = (e.get("links") or {}).get("pia")
    if u:
        out.append(u)
    for t in e.get("tickets") or []:
        u = t.get("url") or ""
        if "pia.jp" in u:
            out.append(u)
    for u in out:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k not in seen:
            seen.add(k)
            uniq.append(u)
    return uniq


build_in, buf = [], []
for i in ids:
    e = by.get(i)
    if not e:
        buf.append("SKIP id=%s（現物に無い）" % i)
        continue
    urls = pia_urls(e)
    if not urls:
        buf.append("SKIP id=%s %s（ぴあURLが無い）" % (i, e.get("name", "")[:34]))
        continue
    build_in.append({"newid": i, "artist": e.get("artist") or e.get("name") or "", "urls": urls})
    buf.append("id=%-5s %-38s ぴあURL%d本" % (i, e.get("name", "")[:38], len(urls)))

json.dump(build_in, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open(OUT.rsplit(".", 1)[0] + ".txt", "w", encoding="utf-8").write("\n".join(buf))
print("TARGETS=%d URLS=%d -> %s" % (len(build_in), sum(len(b["urls"]) for b in build_in), OUT))
