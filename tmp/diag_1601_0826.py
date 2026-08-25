# -*- coding: utf-8 -*-
"""build_pia_entries は2枠取れたのに reconcile_pia は「買える枠0」と言う。
どちらが正しいのか、保存済みの実HTMLに parse_cards を直接当てて確かめる（通信なし）。"""
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe

h = open("tmp/pia_1601.html", encoding="utf-8", errors="replace").read()

print("is_error_page =", bpe.is_error_page(h))
print("wpia_only     =", bpe.wpia_only(h))
print("")
cards = bpe.parse_cards(h)
print("parse_cards が返したカード数 =", len(cards))
for r in cards:
    suf, iso, sd = bpe.parse_when(r["state"], r["when"])
    print("  state=%-6s title=%-30s when=%-30s → suf=%s iso=%s sd=%s" % (
        r.get("state"), (r.get("title") or "")[:30], (r.get("when") or "")[:30], suf, iso, sd))
    print("      perfdate=%s prefs=%s url=%s" % (r.get("perfdate"), r.get("prefs"), r.get("url")))
