# -*- coding: utf-8 -*-
"""check_zero_badge が出す「公演まで31日より先なのに買える枠が0」を型ごとに仕分ける。

🚨 これは**削除候補ではない**（DELETE_GATE 2.）。どれも「なぜ買える枠が無いのか」の理由が違う。
   ネットは叩かない＝現物の tickets だけで分類する。
"""
import re, json, io, datetime

TODAY = datetime.date.today()
TODAY_S = TODAY.isoformat()

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY_S) and d < TODAY_S)


def to_date(s):
    try:
        y, m, d = (s or "").split("-")
        return datetime.date(int(y), int(m), int(d))
    except Exception:
        return None


SENKO = re.compile(r"(先行|プレリザーブ|プレオーダー|プリセール|先着先行|最速|抽選)")
IPPAN = re.compile(r"(一般発売|一般販売|当日券|当日引換)")

buckets = {}
rows = []
for e in EV:
    if e.get("genre") == "new":
        continue
    d = to_date(e.get("date"))
    if not d or (d - TODAY).days <= 30:
        continue
    tks = e.get("tickets") or []
    if any(visible(t) for t in tks):
        continue
    types = [t.get("type") or "" for t in tks]
    L = e.get("links") or {}
    vendors = [k for k in ("pia", "eplus", "rakuten", "lawson") if L.get(k)]
    has_ippan = any(IPPAN.search(x) for x in types)
    has_senko = any(SENKO.search(x) for x in types)
    if not tks:
        b = "E 枠が1つも無い"
    elif has_senko and not has_ippan:
        b = "A 先行だけ登録・一般発売がまだ立っていない"
    elif has_ippan and all((t.get("date") or "") < TODAY_S for t in tks):
        # 一般発売はあるが締切が全部過去＝発売済みで締切が取れていない（ヒール漏れ）か本当に終了
        same = sum(1 for t in tks if t.get("startDate") and t.get("startDate") == t.get("date"))
        b = "B ヒール漏れ（startDate==date）" if same else "C 一般発売の締切が全部過去"
    else:
        b = "D その他"
    buckets.setdefault(b, []).append(e["id"])
    rows.append((b, (d - TODAY).days, e["id"], e.get("genre"), e.get("name", "")[:40],
                 "+".join(vendors) or "売り手なし", len(tks), types[:3]))

rows.sort(key=lambda r: (r[0], r[1]))
buf = ["「公演まで31日より先なのに買える枠が0」の内訳（today=%s）" % TODAY_S, ""]
for b in sorted(buckets):
    buf.append("  %s … %d件" % (b, len(buckets[b])))
buf.append("")
for b, days, i, g, nm, v, n, ts in rows:
    buf.append("%s | あと%3d日 id=%-5s [%-9s] %s" % (b[0], days, i, g or "", nm))
    buf.append("        売り手=%s 枠%d  %s" % (v, n, " / ".join(ts)))
io.open("tmp/zero_class_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("TOTAL=%d  %s" % (len(rows), {k: len(v) for k, v in sorted(buckets.items())}))
