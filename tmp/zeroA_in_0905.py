# -*- coding: utf-8 -*-
"""「買える枠0・A型（先行だけ登録・一般発売がまだ）」の53件について、
build_pia_entries に渡す入力（そのエントリの**ぴあURL全部**）を作る。ネットは叩かない。

🚨 URLは1本だけ渡すと multi=False になって ticket.url が刻まれない
   （[[feedback_build_pia_multiurl_loses_ticket_url]]）。必ず既存の全URLを渡す。
🚨 ぴあURLが1本も無いエントリは対象外（取り直せない＝他社/公式を見るしかない）。
"""
import re, json, io, datetime

TODAY = datetime.date.today()
TODAY_S = TODAY.isoformat()
SENKO = re.compile(r"(先行|プレリザーブ|プレオーダー|プリセール|最速|抽選)")
IPPAN = re.compile(r"(一般発売|一般販売|当日券|当日引換)")

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY_S) and d < TODAY_S)


def to_date(s):
    try:
        y, m, d = (s or "").split("-")
        return datetime.date(int(y), int(m), int(d))
    except Exception:
        return None


def pia_urls(e):
    out = []
    u = (e.get("links") or {}).get("pia")
    if u:
        out.append(u)
    for t in e.get("tickets") or []:
        u = t.get("url") or ""
        if "pia.jp" in u:
            out.append(u)
    seen, uniq = set(), []
    for u in out:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k not in seen:
            seen.add(k)
            uniq.append(u)
    return uniq


build_in, nopia, buf = [], [], []
for e in EV:
    if e.get("genre") == "new":
        continue
    d = to_date(e.get("date"))
    if not d or (d - TODAY).days <= 30:
        continue
    tks = e.get("tickets") or []
    if not tks or any(visible(t) for t in tks):
        continue
    types = [t.get("type") or "" for t in tks]
    if not (any(SENKO.search(x) for x in types) and not any(IPPAN.search(x) for x in types)):
        continue          # A型だけ
    urls = pia_urls(e)
    if not urls:
        nopia.append((e["id"], e.get("name", "")[:38]))
        continue
    build_in.append({"newid": e["id"], "artist": e.get("artist") or e.get("name") or "", "urls": urls})
    buf.append("id=%-5s URL%d  %s" % (e["id"], len(urls), e.get("name", "")[:44]))

json.dump(build_in, io.open("tmp/zeroA_in_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
buf.append("")
buf.append("ぴあURLが無くて取り直せない: %d件" % len(nopia))
for i, nm in nopia:
    buf.append("   id=%-5s %s" % (i, nm))
io.open("tmp/zeroA_in_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("A_TARGETS=%d (URL合計 %d) / NO_PIA=%d" % (len(build_in), sum(len(b["urls"]) for b in build_in), len(nopia)))
