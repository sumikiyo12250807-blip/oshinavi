# -*- coding: utf-8 -*-
"""振り分けの直前に、新着プールの「公演名＋割り当てジャンル＋URL」の一覧を
logs/assigned_YYYY-MM-DD.md に書き出す（振り分けると _genre が消えるので先に作る）。
使い方: python tmp/assign_log_0905.py [--note "..."]"""
import json, re, io, sys, datetime

TODAY = datetime.date.today().isoformat()
OUT = "logs/assigned_%s.md" % TODAY

GENRE_LABEL = {}
html = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"const GENRE_LABEL = \{(.*?)\};", html, re.S)
if m:
    for k, v in re.findall(r"(\w+)\s*:\s*\"([^\"]+)\"", m.group(1)):
        GENRE_LABEL[k] = v

events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
news = sorted([e for e in events if e.get("genre") == "new"], key=lambda e: e["id"])

note = ""
if "--note" in sys.argv:
    note = sys.argv[sys.argv.index("--note") + 1]

rows = []
cnt = {}
for e in news:
    g = e.get("_genre") or "(未定)"
    cnt[g] = cnt.get(g, 0) + 1
    links = e.get("links") or {}
    url = links.get("pia") or links.get("eplus") or links.get("rakuten") or links.get("lawson") or ""
    rows.append("| %s | %s | %s | %s | %s | %s |"
                % (e["id"], e.get("name", ""), GENRE_LABEL.get(g, g), e.get("venue", "")[:40],
                   e.get("date", ""), ("[ページ](%s)" % url) if url else "-"))

buf = ["# %s 新着の振り分け" % TODAY, ""]
if note:
    buf += [note, ""]
buf += ["振り分けた件数＝**%d件**（ぴあ由来のみ）。ジャンル内訳＝%s"
        % (len(news), "／".join("%s %d" % (GENRE_LABEL.get(k, k), v)
                                for k, v in sorted(cnt.items(), key=lambda x: -x[1]))), ""]
buf += ["| id | 公演名 | ジャンル | 会場 | 公演日 | 確認用 |", "|---|---|---|---|---|---|"]
buf += rows
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("WROTE %s rows=%d" % (OUT, len(rows)))
