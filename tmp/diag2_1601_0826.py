# -*- coding: utf-8 -*-
"""build_pia_entries 自身の fetch でページを取り直し、parse_cards と build() の両方を見る。
curl で取った HTML では「受付終了1枚」しか無かったのに build は2枠作った。どこで差が出たのかを見る。"""
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe

URL = "https://t.pia.jp/pia/event/event.do?eventCd=2625347"

h = bpe.fetch(URL)
print("fetch bytes =", len(h))
print("is_error_page =", bpe.is_error_page(h), " wpia_only =", bpe.wpia_only(h))
cards = bpe.parse_cards(h)
print("parse_cards =", len(cards))
for r in cards:
    suf, iso, sd = bpe.parse_when(r["state"], r["when"])
    print("  state=%-6s title=%-28s perfdate=%s suf=%s url=%s" % (
        r.get("state"), (r.get("title") or "")[:28], r.get("perfdate"), suf, r.get("url")))

print("")
print("=== build() が何を作るか ===")
try:
    ent = bpe.build([URL])
    print(type(ent))
    if isinstance(ent, dict):
        for t in ent.get("tickets") or []:
            print("  -", t)
    else:
        print(ent)
except Exception as ex:
    print("build 失敗:", type(ex).__name__, str(ex)[:200])
