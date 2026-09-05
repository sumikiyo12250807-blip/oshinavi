# -*- coding: utf-8 -*-
"""独立検証で見つかった「index.htmlのどこにも無い買える枠」を、既存エントリへ統合するための
build_pia_entries 入力を作る。

🚨 入力は「そのエントリの**既存ぴあURL全部** ＋ 今日見つかった新URL」を渡す
   （1本だけ渡すと multi=False で ticket.url が刻まれない
    ＝[[feedback_build_pia_multiurl_loses_ticket_url]]）。
🚨 「掲載あり」と出たもの（橘花怜ソロ／蓮見翔／猫森集会）は**別エントリの公演**なので入れない。
🚨 買える枠が0のページは足しても枠が増えないので入れない（fetchを増やすだけ）。
"""
import re, json, io

# 検証で出た「買える枠がある未掲載ページ」
ADD = {
    722:  ["2613327", "2614332", "2614684", "2616975", "2611910", "2610711", "2612588", "2614216"],
    177:  ["2615341", "2618030", "2618031", "2617854", "2621767", "2622063", "2621630", "2626652", "2629853"],
    1149: ["2633498"],
    4235: ["2632194", "2631960"],
    4797: ["2624103"],
    5251: ["2620308"],
    632:  ["2618708"],
    2876: ["2628306"],
}

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}


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


build_in, buf = [], []
for i, cds in sorted(ADD.items()):
    e = by.get(i)
    if not e:
        buf.append("SKIP id=%s（現物に無い）" % i)
        continue
    urls = pia_urls(e)
    have = set()
    for u in urls:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        if mm:
            have.add(mm.group(1))
    add = ["https://t.pia.jp/pia/event/event.do?eventCd=%s" % c for c in cds if c not in have]
    if not add:
        buf.append("SKIP id=%s %s（新URLが全部すでに登録済み）" % (i, e.get("name", "")[:30]))
        continue
    build_in.append({"newid": i, "artist": e.get("artist") or e.get("name") or "",
                     "urls": urls + add})
    buf.append("id=%-5s %s | 既存URL%d + 追加%d" % (i, e.get("name", "")[:34], len(urls), len(add)))

json.dump(build_in, io.open("tmp/extra_in_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open("tmp/extra_in_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("TARGETS=%d URLS=%d -> tmp/extra_in_0905.json" % (len(build_in), sum(len(b["urls"]) for b in build_in)))
