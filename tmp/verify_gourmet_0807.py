# -*- coding: utf-8 -*-
"""グルメ新設と振り分けの結果を機械で確認する（2026-08-07）。
 ①gourmetの4か所が揃っているか ②3926がgourmetになったか ③新着プールが0件か
 ④下書きフィールドが残っていないか ⑤ジャンル別件数
"""
import collections
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

h = io.open(r"C:\Users\user\oshinavi\index.html", encoding="utf-8").read()
ai = io.open(r"C:\Users\user\oshinavi\tools\build_ai_page.py", encoding="utf-8").read()

print("① 実装4か所")
print("   フィルタボタン : %s" % ("OK" if 'data-genre="gourmet"' in h else "🚨無い"))
print("   バッジ色CSS    : %s" % ("OK" if ".genre-gourmet" in h else "🚨無い"))
print("   GENRE_LABEL(html): %s" % ("OK" if re.search(r'gourmet:\s*"グルメ"', h) else "🚨無い"))
print("   GENRE_LABEL(ai) : %s" % ("OK" if '"gourmet": "グルメ"' in ai else "🚨無い"))

evs = extract_events_array(r"C:\Users\user\oshinavi\index.html")
by = {e["id"]: e for e in evs}
e = by.get(3926)
print("\n② 3926 のジャンル: %s / extraGenres=%s" % (e.get("genre"), e.get("extraGenres")))

pool = [x for x in evs if x.get("genre") == "new"]
m = re.search(r"const NEW_ORDER = (\[[^\]]*\]);", h)
print("③ 新着プール %d件 / NEW_ORDER=%s" % (len(pool), m.group(1) if m else "?"))

draft = [x["id"] for x in evs if any(k in x for k in ("_genre", "_extraGenres", "_piaSub", "_srcgenre"))]
print("④ 下書きフィールドが残っているエントリ: %d件 %s" % (len(draft), draft[:10]))

new50 = [x for x in evs if 3877 <= x["id"] <= 3926]
c = collections.Counter(x.get("genre") for x in new50)
print("\n⑤ 今日の50件のジャンル内訳（%d件）" % len(new50))
for k, v in c.most_common():
    print("   %-10s %d" % (k, v))
ex = [(x["id"], x.get("genre"), x.get("extraGenres")) for x in new50 if x.get("extraGenres")]
print("   両方方式 %d件: %s" % (len(ex), ex))
print("\n全%d件 / gourmet全体 %d件" % (len(evs), sum(1 for x in evs if x.get("genre") == "gourmet")))
