# -*- coding: utf-8 -*-
"""ぴあページの券種カードを parse_cards でそのまま全部出す（畳まない前の姿を見る）。

🚨 `pia_tickets.py` は「レスポンシブで各カードが2回出る」ぶんを重複除去するが、
   **券種名が同じで売り場コードだけ違う別枠まで畳む**ことがある（2026-09-05 id2254 の3次受付で発覚）。
   これは畳む前の生データを見るための道具。

使い方: python tmp/cards_dump_0905.py <eventCd|URL> [...]
"""
import io, sys, time
sys.path.insert(0, "tools")
from build_pia_entries import fetch, parse_cards, slot_code

buf = []
for a in sys.argv[1:]:
    url = a if a.startswith("http") else "https://t.pia.jp/pia/event/event.do?eventCd=%s" % a
    buf.append("■ %s" % url)
    try:
        h = fetch(url)
    except Exception as e:
        buf.append("   取得できなかった: %s: %s" % (e.__class__.__name__, e))
        buf.append("")
        continue
    cards = parse_cards(h)
    buf.append("   カード %d枚" % len(cards))
    seen = {}
    for c in cards:
        code = ""
        try:
            code = slot_code(c.get("url") or "") or ""
        except Exception:
            pass
        key = (c.get("title"), c.get("state"), c.get("when"))
        seen.setdefault(key, []).append(code)
        buf.append("   [%s] %s" % (c.get("state"), c.get("title")))
        buf.append("        when=%s" % (c.get("when") or "(空)"))
        buf.append("        売り場コード=%s  url=%s" % (code or "(なし)", c.get("url") or "(なし)"))
    buf.append("")
    buf.append("   ▼ 同じ(券種名,状態,期間)で売り場コードが複数あるもの＝畳むと消える枠")
    for k, codes in seen.items():
        u = sorted(set(x for x in codes if x))
        if len(u) > 1:
            buf.append("   🚨 %s | %s | %s → コード%d個 %s" % (k[0], k[1], k[2] or "", len(u), u))
    buf.append("")
    time.sleep(1.0)

io.open("tmp/cards_dump_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/cards_dump_0905.txt (%d lines)" % len(buf))
