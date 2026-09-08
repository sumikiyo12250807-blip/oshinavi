# -*- coding: utf-8 -*-
"""楽天が「売り切れ」と「販売終了」をどう書き分けているかを、実ページから調べる。

🚨ぴあは `pia_statustext.py` で生HTMLの文言（予定枚数終了／販売終了）を読んで打ち分けている。
   楽天には同じ道具が無い＝[[feedback_saleended_vs_soldout]] の判定が楽天枠でできない。
   まず「そもそも楽天のHTMLにその情報があるか」を確かめる。
"""
import io, re, sys, json, time, collections
sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")
import rakuten_harvest as R

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

# 楽天の素URLを集める（Deep Linkからは murl を取り出す）
import urllib.parse
urls = []
for e in EV:
    cands = [(e.get("links") or {}).get("rakuten") or ""]
    cands += [(t.get("url") or "") for t in (e.get("tickets") or [])]
    for u in cands:
        if not u:
            continue
        if "linksynergy" in u:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
            u = (q.get("murl") or [""])[0]
        if u.startswith("https://ticket.rakuten.co.jp/") and u not in urls:
            urls.append(u)

o = io.open("tmp/rk_status_probe_0908.md", "w", encoding="utf-8")
o.write("# 楽天は「売り切れ」と「販売終了」を書き分けているか\n\n")
o.write("登録から拾った楽天の素URL＝%d件。先頭8件を実際に取って文言を数える。\n\n" % len(urls))
o.write("| # | ページ | 予定枚数終了 | 完売 | 売切 | 販売終了 | 受付終了 | SOLD OUT | active数 |\n")
o.write("|---|---|---|---|---|---|---|---|---|\n")

WORDS = ["予定枚数終了", "完売", "売切", "販売終了", "受付終了", "SOLD"]
tot = collections.Counter()
for i, u in enumerate(urls[:8], 1):
    try:
        b = R.fetch(u)
    except Exception as ex:
        o.write("| %d | %s | 取得失敗 | | | | | | |\n" % (i, u.rstrip("/").split("/")[-1]))
        time.sleep(1)
        continue
    counts = [b.count(w) for w in WORDS]
    for w, c in zip(WORDS, counts):
        tot[w] += c
    act = len(re.findall(r"performance[^'\"]*active", b))
    o.write("| %d | %s | %s | %d |\n" % (i, u.rstrip("/").split("/")[-1],
                                          " | ".join(str(c) for c in counts), act))
    time.sleep(1)

o.write("\n## 合計\n\n")
for w in WORDS:
    o.write("- %s … %d回\n" % (w, tot[w]))
o.close()
print("urls=%d -> tmp/rk_status_probe_0908.md  %s" % (len(urls), dict(tot)))
