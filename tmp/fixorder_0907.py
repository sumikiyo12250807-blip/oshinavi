# -*- coding: utf-8 -*-
"""NEW_ORDER から、削除した20件のidを外してプールと一致させる。

delete_entries.py は EVENTS 配列しか触らないので、NEW_ORDER に消したidが残る
（feedback_new_order_array＝新着タブに「もう新着でないもの」が出る／並びがズレる）。
🚨 定義行を丸ごと置換するので、書いたあと必ず grep 2本と突合を通す。
"""
import io, re, json

PATH = "index.html"
src = io.open(PATH, encoding="utf-8", newline="").read()

EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", src, re.S).group(1))
pool = set(e["id"] for e in EV if e.get("genre") == "new")

m = re.search(r"(const NEW_ORDER = )(\[[^\]]*\])(;)", src, re.S)
assert m, "NEW_ORDER が見つからない"
arr = json.loads(m.group(2))
kept = [i for i in arr if i in pool]
print("NEW_ORDER %d → %d（外す %d）" % (len(arr), len(kept), len(arr) - len(kept)))

new_def = m.group(1) + json.dumps(kept, separators=(", ", ": ")) + m.group(3)
out = src[:m.start()] + new_def + src[m.end():]

io.open("index.html.bak_0907_order", "w", encoding="utf-8", newline="").write(src)
io.open(PATH, "w", encoding="utf-8", newline="").write(out)

# 検算
h = io.open(PATH, encoding="utf-8", newline="").read()
EV2 = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool2 = set(e["id"] for e in EV2 if e.get("genre") == "new")
arr2 = json.loads(re.search(r"const NEW_ORDER = (\[[^\]]*\])", h, re.S).group(1))
print("プール=%d / NEW_ORDER=%d / 一致=%s" % (len(pool2), len(arr2), set(arr2) == pool2))
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
