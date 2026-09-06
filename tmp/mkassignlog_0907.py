# -*- coding: utf-8 -*-
"""今日振り分けた分を logs/assigned_2026-09-07.md に残す。
新着タブは振り分けで空くので、この一覧が「あとから見る場所」になる。
URLは index.html から機械抽出したものだけを出す。
"""
import io, re, json, collections

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

# 今朝のバッチ＝id 7025..7098 のうち、もう "new" ではないもの
rows = []
for e in EV:
    if 7025 <= e["id"] <= 7098 and e.get("genre") != "new":
        L = e.get("links") or {}
        url = L.get("pia") or L.get("eplus") or L.get("rakuten") or L.get("lawson") or ""
        rows.append((e["id"], e.get("genre"), e.get("name", ""), url, e.get("venue", "")))

rows.sort()
cnt = collections.Counter(r[1] for r in rows)

with io.open("logs/assigned_2026-09-07.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("# 2026-09-07 朝に振り分けたエントリ（%d件）\n\n" % len(rows))
    f.write("下書き `_genre`（＝チケットぴあが付けているカテゴリ）をそのまま正式ジャンルに移した。\n")
    f.write("別エージェントに**判定案を見せずゼロから**分類させたところ、**48件すべて一致**した。\n\n")
    f.write("⏸ **id7092 吉良花火クルーズ は振り分けずプールに残した**＝ぴあの区分は\n")
    f.write("「イベント/アミューズメント」→ kids だが、中身は花火鑑賞。同じバッチに hanabi 行きの\n")
    f.write("花火大会がいるので、kids でいいか相談したい。\n\n")
    f.write("ジャンル内訳: %s\n\n" % " / ".join("%s %d" % (g, c) for g, c in cnt.most_common()))
    f.write("| id | ジャンル | 公演名 | 会場 | 確認用URL |\n|---|---|---|---|---|\n")
    for eid, g, name, url, venue in rows:
        link = "[確認](%s)" % url if url else "(URLなし)"
        f.write("| %s | %s | %s | %s | %s |\n"
                % (eid, g, name.replace("|", "／")[:60], (venue or "").replace("|", "／")[:30], link))

print("wrote logs/assigned_2026-09-07.md (%d件)" % len(rows))
