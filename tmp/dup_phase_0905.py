# -*- coding: utf-8 -*-
"""同じ販売枠が「発売前の形」と「販売中の形」で2枚残っているエントリを数える。

🚨 これは `tools/check_dup_slots.py` が拾えていない型（2026-09-05 杉山清貴2254で発覚）。
   例＝同じ url・同じ券種名で
     「一般発売（東京 12/5〜12/6公演）**9/4 10:00発売**」（発売前の形・締切がstartDateのまま）
     「一般発売（東京 12/5〜12/6公演）**〜12/2 23:59**」（ヒール後の正しい形）
   の2枚。画面には同じ文言のバッジが2行並ぶ。
   ＝ヒール/取り直しが**新しい形を足したのに古い形を消さなかった**残骸。

出力: tmp/dup_phase_0905.txt
"""
import re, json, io, datetime

TODAY = datetime.date.today().isoformat()
h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))

RE_SALE = re.compile(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$")   # 発売前の形
RE_END = re.compile(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$")      # 販売中の形


def base(ty):
    ty = RE_END.sub("", ty or "")
    ty = RE_SALE.sub("", ty)
    return ty.strip()


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


rows, n_pairs, n_entries = [], 0, 0
for e in EV:
    groups = {}
    for t in e.get("tickets") or []:
        groups.setdefault((base(t.get("type")), (t.get("url") or "").strip()), []).append(t)
    hits = []
    for (bt, u), ts in groups.items():
        if len(ts) < 2:
            continue
        pre = [t for t in ts if RE_SALE.search(t.get("type") or "")]
        liv = [t for t in ts if RE_END.search(t.get("type") or "")]
        if pre and liv:
            hits.append((bt, u, pre, liv))
    if not hits:
        continue
    n_entries += 1
    n_pairs += len(hits)
    rows.append("■ id=%-5s %s" % (e["id"], e.get("name", "")[:44]))
    for bt, u, pre, liv in hits:
        rows.append("    枠: %s" % bt)
        rows.append("      飛び先: %s" % (u or "(なし＝カード共通リンク)"))
        for t in pre:
            rows.append("      🕐発売前の形  %s  (締切=%s 開始=%s 表示=%s)"
                        % (t.get("type"), t.get("date"), t.get("startDate"), "出る" if visible(t) else "出ない"))
        for t in liv:
            rows.append("      ✅販売中の形  %s  (締切=%s 表示=%s)"
                        % (t.get("type"), t.get("date"), "出る" if visible(t) else "出ない"))
    rows.append("")

buf = ["同じ枠が「発売前の形」と「販売中の形」で2枚残っているもの（today=%s）" % TODAY,
       "  エントリ %d件 / 枠 %d組" % (n_entries, n_pairs), ""] + rows
io.open("tmp/dup_phase_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("ENTRIES=%d PAIRS=%d -> tmp/dup_phase_0905.txt" % (n_entries, n_pairs))
