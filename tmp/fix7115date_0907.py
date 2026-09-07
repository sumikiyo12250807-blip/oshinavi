# -*- coding: utf-8 -*-
"""id7115 Tani Yuuki の date / dateLabel / venue / prefecture を、ぴあ再ビルドの値に揃える。

枠を4つ足して公演範囲が広がったのに、エントリは北海道12/4のままだった。
reconcile の QC-EVDATE が「ev.date が実公演の千秋楽より古い＝画面から消える」と検知したもの。

🚨 値の書き換えなので行置換（json.dumps で配列を作り直さない）。
🚨 値は built JSON から機械で移す（化けた出力を目で写さない）。
"""
import io, re, json

built = json.load(io.open("tmp/built_7115_0907.json", encoding="utf-8"))[0]
NEW = {k: built[k] for k in ("date", "dateLabel", "venue", "prefecture")}

PATH = "index.html"
src = io.open(PATH, encoding="utf-8", newline="").read()
lines = src.split("\r\n")

cur, done = None, {}
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id": (\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur == 7115:
        for k, v in NEW.items():
            m2 = re.match(r'(\s*"%s": )(.*?)(,?)$' % k, ln)
            if m2 and k not in done:
                lines[i] = m2.group(1) + json.dumps(v, ensure_ascii=False) + m2.group(3)
                done[k] = True

assert set(done) == set(NEW), "書き換えられなかったフィールド: %s" % (set(NEW) - set(done))

io.open("index.html.bak_0907_7115", "w", encoding="utf-8", newline="").write(src)
io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

h = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
e = [x for x in EV if x["id"] == 7115][0]
ok = all(e.get(k) == v for k, v in NEW.items())
print("4フィールドを更新 / 検算=%s / date=%s" % (ok, e["date"]))
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
