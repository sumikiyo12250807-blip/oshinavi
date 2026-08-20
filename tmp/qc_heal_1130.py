# -*- coding: utf-8 -*-
"""ヒール適用後のQC＋削除候補11件の詳細（URLは index.html の links から機械抽出のみ）。"""
import io
import json
import re
import sys
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = r"C:\Users\user\oshinavi\index.html"
TODAY = datetime.date.today().isoformat()

raw = open(P, "rb").read()
crlf = raw.count(b"\r\n")
lf = raw.count(b"\n")
print("=== 改行チェック ===")
print("  CRLF %d / 単独LF %d  → %s" % (crlf, lf - crlf, "OK" if lf - crlf == 0 else "🚨LF混入"))

h = raw.decode("utf-8")
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
evs = json.loads(m.group(2))
by_id = {e["id"]: e for e in evs}

# 隠れ枠の残り
def is_stale(t):
    sd, d = t.get("startDate"), t.get("date")
    return bool(sd and sd == d and d <= TODAY and not t.get("saleUntilSoldOut"))

hidden = [(e["id"], sum(1 for t in (e.get("tickets") or []) if is_stale(t))) for e in evs]
hidden = [(i, n) for i, n in hidden if n]
print("\n=== 隠れ枠の残り ===")
print("  %d エントリ / %d 枠（適用前は 197エントリ・310枠）" % (len(hidden), sum(n for _, n in hidden)))

CAND = [2166, 2172, 2433, 2437, 2461, 2536, 2706, 2857, 2858, 3145, 3248]

def visible(t):
    """index.html renderCard の非表示判定を機械で当てる:
       if ((!startDate || startDate<=today) && date<today) return ''"""
    sd, d = t.get("startDate"), t.get("date")
    if (not sd or sd <= TODAY) and (d or "") < TODAY:
        return False
    return True

print("\n=== 削除候補 11件の詳細 ===")
for cid in CAND:
    e = by_id.get(cid)
    if not e:
        print("id=%s 見つからない" % cid)
        continue
    links = e.get("links") or {}
    pia = links.get("pia") or ""
    tickets = e.get("tickets") or []
    vis = [t for t in tickets if visible(t)]
    # 今日が発売日で、まだ発売時刻が来ていない可能性のある枠
    today_sale = [t for t in tickets if t.get("startDate") == TODAY]
    times = []
    for t in today_sale:
        mm = re.search(r"(\d{1,2}):(\d{2})\s*発売", t.get("type") or "")
        if mm:
            times.append("%s:%s発売" % (mm.group(1), mm.group(2)))
    print("\n■ id=%s %s" % (cid, e.get("name")))
    print("   %s / 公演 %s / 全%d枠・画面に出る枠 %d" % (
        e.get("prefecture"), e.get("date"), len(tickets), len(vis)))
    print("   販売先: %s" % ",".join(sorted(links.keys())))
    if today_sale:
        print("   ⚠️本日(%s)発売の枠が %d件 %s" % (TODAY, len(today_sale), ("／".join(times)) if times else "（時刻表記なし）"))
    if pia:
        print("   確認URL: %s" % pia)
    else:
        print("   🚨ぴあURL無し＝機械照合が効かない（最警戒）")
