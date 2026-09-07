# -*- coding: utf-8 -*-
"""id7092 吉良花火クルーズ の下書きジャンルを kids → hanabi に直す。

ユーザー判断（2026-09-07）＝「お出かけに花火があるでしょ」
＝ hanabi は odekake グループにあるので、花火鑑賞はそこへ入れる。
ぴあの区分は「イベント/アミューズメント」（クルーズ船という"器"を見た分類）だが、
主役は花火なので読み直す＝feedback_genre_pia_asis_and_other の例外2。

🚨 値の書き換えなので行置換（json.dumps で配列を作り直さない）。読み書きとも newline=''。
あわせて、このあと assign_genres.py に渡す「除外id」（7092以外のプール全部）も出す。
"""
import io, re, json, sys

PATH = "index.html"
APPLY = "--apply" in sys.argv

src = io.open(PATH, encoding="utf-8", newline="").read()
lines = src.split("\r\n")

cur, n = None, 0
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id": (\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur == 7092:
        m2 = re.match(r'(\s*"_genre": )(.*?)(,?)$', ln)
        if m2:
            lines[i] = m2.group(1) + '"hanabi"' + m2.group(3)
            n += 1
            cur = None

assert n == 1, "_genre の行が %d 個（1個のはず）" % n

if APPLY:
    io.open("index.html.bak_0907_7092", "w", encoding="utf-8", newline="").write(src)
    io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

h = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}
print("id7092 _genre=%r genre=%r" % (by[7092].get("_genre"), by[7092].get("genre")))

pool = [e["id"] for e in EV if e.get("genre") == "new"]
skip = sorted(x for x in pool if x != 7092)
io.open("tmp/excl7092_0907.txt", "w", encoding="utf-8").write(",".join(str(x) for x in skip))
print("プール%d / 振り分け1件(7092) / 除外%d件 → tmp/excl7092_0907.txt" % (len(pool), len(skip)))
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
