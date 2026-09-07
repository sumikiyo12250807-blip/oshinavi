# -*- coding: utf-8 -*-
"""指定エントリの date（＝千秋楽）を直す。枠を足して公演範囲が広がった時に使う。

reconcile の ❌QC-EVDATE「ev.date が実公演の千秋楽より古い＝画面から消える」への対処。
🚨 値の書き換えなので行置換（json.dumps で配列を作り直さない）。読み書きとも newline=''。

使い方: python tmp/fixdate_0907.py <id>=<YYYY-MM-DD> [<id>=<YYYY-MM-DD> ...] [--apply]
"""
import io, re, json, sys

APPLY = "--apply" in sys.argv
NEW = {}
for a in sys.argv[1:]:
    if "=" in a:
        k, v = a.split("=", 1)
        NEW[int(k)] = v
assert NEW, "id=日付 を1つ以上渡して"

PATH = "index.html"
src = io.open(PATH, encoding="utf-8", newline="").read()
lines = src.split("\r\n")

cur, done = None, {}
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id": (\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur in NEW and cur not in done:
        m2 = re.match(r'(\s*"date": )(.*?)(,?)$', ln)
        if m2:
            print("id=%s date %s → %s" % (cur, m2.group(2), json.dumps(NEW[cur])))
            lines[i] = m2.group(1) + json.dumps(NEW[cur]) + m2.group(3)
            done[cur] = True

assert set(done) == set(NEW), "見つからなかったid: %s" % (set(NEW) - set(done))

if not APPLY:
    print("(--apply で書き込む)")
    sys.exit(0)

io.open("index.html.bak_0907_fixdate", "w", encoding="utf-8", newline="").write(src)
io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

h = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}
for k, v in NEW.items():
    print("検算 id=%s date=%s %s" % (k, by[k]["date"], "OK" if by[k]["date"] == v else "🚨ちがう"))
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
