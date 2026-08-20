# -*- coding: utf-8 -*-
"""新田恵海の先行2枠のURLを、抽選申込ページ(lotRlsCd)から公演ページ(eventCd)へ差し替える。

lotRlsCd の個別ページは券種カードを持たない別レイアウトで、しかも 429 になりやすい。
ticket.url に入れておくと reconcile が毎回そこを叩いて ❌FETCH で赤くなる（実害＝8/6のゲート）。
昼／夜の区別はバッジの〔昼公演〕〔夜公演〕で付くので、URLは公演ページで足りる。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_nitta_url"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

EV = "https://t.pia.jp/pia/event/event.do?eventCd=2627798"
n = 0
for e in EVENTS:
    if e["id"] != 3811:
        continue
    for t in e.get("tickets") or []:
        if "lotRlsCd" in (t.get("url") or ""):
            t["url"] = EV
            n += 1
assert n == 2, "差し替えたのは%d枠（2のはず）" % n

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("新田恵海の先行2枠のURLを公演ページに差し替えた")
