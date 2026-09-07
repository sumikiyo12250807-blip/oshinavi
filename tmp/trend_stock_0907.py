# -*- coding: utf-8 -*-
"""Xのトレンドに出た名前が、OSHINAVIに「いま買える枠」として載っているかを見る。
🚨 判定は index.html の実物の表示ルールと同じ形（soldout/saleUntilSoldOut は常に表示）。
"""
import io, re, json

TODAY = "2026-09-07"
WORDS = ["SPY×FAMILY", "スパイファミリー", "斉藤和義"]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


with io.open("tmp/trend_stock_0907.txt", "w", encoding="utf-8") as f:
    for w in WORDS:
        f.write("=== 「%s」 ===\n" % w)
        n = 0
        for e in EV:
            blob = (e.get("name") or "") + " " + (e.get("artist") or "")
            if w not in blob:
                continue
            n += 1
            alive = [t for t in e.get("tickets", []) if visible(t)]
            f.write("  id=%-6s [%-9s] 公演%s 生き枠%d/%d  %s\n"
                    % (e["id"], e.get("genre"), e.get("date"), len(alive),
                       len(e.get("tickets", [])), (e.get("name") or "")[:44]))
            f.write("     会場: %s\n" % (e.get("venue") or "")[:50])
            for t in alive:
                f.write("     ○ %s | %s\n" % ((t.get("type") or "")[:52], (t.get("url") or "")[:60]))
        if not n:
            f.write("  （該当なし）\n")
        f.write("\n")
print("wrote tmp/trend_stock_0907.txt")
