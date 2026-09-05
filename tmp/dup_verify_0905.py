# -*- coding: utf-8 -*-
"""「発売前の形」と「販売中の形」が2枚並んでいるエントリを、ぴあの実ページと突き合わせる。

判定＝**ぴあの買える枠の数**と**登録の可視枠の数**を比べる：
  ぴあ < 登録  → 重複の疑い（同じ枠が2枚ある）
  ぴあ == 登録 → 正しい2枚（通年券の「次の販売期間」など）。触らない
  ぴあ > 登録  → 取りこぼし（枠が足りない）

🚨 数だけで消さない。この出力は「どれを実ページで見るか」を絞るためのもの。
使い方: python tmp/dup_verify_0905.py [id ...]   （省略時は dup_phase の全件）
"""
import re, json, io, sys, time, datetime

sys.path.insert(0, "tools")
from build_pia_entries import fetch, parse_cards

TODAY = datetime.date.today().isoformat()
DEFAULT_IDS = [2254, 2388, 2395, 3053, 3492, 3501, 3514, 3997, 5014, 5496, 5697, 6136, 6331]
ids = [int(a) for a in sys.argv[1:] if a.isdigit()] or DEFAULT_IDS

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


def pia_urls(e):
    out, seen = [], set()
    u = (e.get("links") or {}).get("pia")
    if u:
        out.append(u)
    for t in e.get("tickets") or []:
        u = t.get("url") or ""
        if "pia.jp" in u:
            out.append(u)
    uniq = []
    for u in out:
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k not in seen:
            seen.add(k)
            uniq.append(u)
    return uniq


buf = []
for i in ids:
    e = by.get(i)
    if not e:
        buf.append("id=%s は現物に無い" % i)
        continue
    vis = [t for t in (e.get("tickets") or []) if visible(t)]
    urls = pia_urls(e)
    buf.append("■ id=%-5s %s" % (i, e.get("name", "")[:44]))
    buf.append("    登録の可視枠 %d / ぴあURL %d本" % (len(vis), len(urls)))
    if not urls:
        buf.append("    🚨ぴあURLが無い（他社由来）＝この方法では判定できない")
        buf.append("")
        continue
    total = 0
    for u in urls:
        try:
            html = fetch(u)
        except Exception as ex:
            buf.append("    ❌ %s: %s" % (ex.__class__.__name__, u))
            continue
        cards = [c for c in parse_cards(html) if c.get("state") in ("受付中", "発売前")]
        total += len(cards)
        buf.append("    %s → 買える%d枠" % (u, len(cards)))
        for c in cards:
            buf.append("        [%s] %s | %s" % (c.get("state"), (c.get("title") or "")[:52], c.get("when") or ""))
        time.sleep(1.0)
    mark = "重複の疑い" if total < len(vis) else ("取りこぼし" if total > len(vis) else "一致＝正しい2枚（触らない）")
    buf.append("    → ぴあ%d枠 vs 登録可視%d枠 … %s" % (total, len(vis), mark))
    buf.append("")

io.open("tmp/dup_verify_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/dup_verify_0905.txt (%d lines)" % len(buf))
