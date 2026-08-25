# -*- coding: utf-8 -*-
"""保存済みのぴあHTMLに parse_cards を当てて、券種カードを全部列挙する（通信なし）。
使い方: python tmp/diag_cards_0826.py tmp/pia_xxx.html [...]"""
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe

for path in sys.argv[1:]:
    h = open(path, encoding="utf-8", errors="replace").read()
    print("=" * 78)
    print(path, " bytes=", len(h), " error_page=", bpe.is_error_page(h), " wpia=", bpe.wpia_only(h))
    cards = bpe.parse_cards(h)
    print("カード数 =", len(cards))
    for r in cards:
        suf, iso, sd = bpe.parse_when(r["state"], r["when"])
        print("  [%-5s] %-34s perf=%-24s suf=%s" % (
            r.get("state"), (r.get("title") or "")[:34], str(r.get("perfdate"))[:24], suf))
        print("          prefs=%s url=%s" % (r.get("prefs"), r.get("url")))
