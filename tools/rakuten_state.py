# -*- coding: utf-8 -*-
"""楽天チケットの「いまの持ち高」を数える。

🚨広い grep だと全エントリが引っかかる＝汎用の楽天ショップ検索ボタンが全カードに付いているから。
   数えるのは **チケットの売り場としての楽天**＝
   links.rakuten か ticket.url が ticket.rakuten.co.jp / linksynergy(mid=53531) を指すもの。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

TICKET = re.compile(r"ticket\.rakuten\.co\.jp|linksynergy\.com/deeplink\?[^\"']*mid=53531")

s = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))

ents, slots, single, invisible, deeplink, bare = [], 0, 0, 0, 0, 0
for e in evs:
    ls = (e.get("links") or {})
    hit = bool(TICKET.search(ls.get("rakuten") or ""))
    ts = []
    for t in e.get("tickets") or []:
        if TICKET.search(t.get("url") or ""):
            ts.append(t)
    if not hit and not ts:
        continue
    ents.append(e["id"])
    slots += len(ts)
    for t in ts:
        # 単日形＝発売日と締切が同じ＝ヒールが要る形（楽天版ヒールが無いので消える）
        if t.get("startDate") and t.get("startDate") == t.get("date"):
            single += 1
    for u in [ls.get("rakuten") or ""] + [t.get("url") or "" for t in ts]:
        if not u:
            continue
        if "linksynergy.com/deeplink" in u:
            deeplink += 1
        elif "ticket.rakuten.co.jp" in u:
            bare += 1

print("楽天チケットのエントリ %d件 / 楽天の販売枠 %d枠" % (len(ents), slots))
print("  うち単日形（発売日＝締切）＝ヒールが要る形: %d枠" % single)
print("  リンクの形: Deep Link %d本 / 素のURL %d本" % (deeplink, bare))
print("  id:", ",".join(str(i) for i in ents))
