# -*- coding: utf-8 -*-
"""「今週のピックアップ」9/6公開号（対象＝9/7(月)〜9/13(日)発売）の素材を確定する。

主役5組＝ABC3軸を1本に組み込む
  A ベテラン       … ASKA / 東京スカパラダイスオーケストラ / 佐藤竹善
  B 全国ツアー一斉 … MONO NO AWARE（10会場を同時に）
  C 年末年始       … 湖月わたる（宝塚退団20周年）
名前タイル＝残りから枠数の多い順に12組。

🚨事実（発売日時・会場・公演日・券種名）はここで機械抽出したものだけを使う。
   音楽的特徴・経歴は別途ウラを取る（[[feedback_x_artist_fact_check]]）。
出力は UTF-8 のテキスト（コンソールは cp932 で化けるので数字だけ出す）。
"""
import json, re, io

FROM, TO = "2026-09-07", "2026-09-13"
MAIN = [4500, 4489, 4236, 668, 4246]     # MONO NO AWARE / ASKA / スカパラ / 佐藤竹善 / 湖月わたる
TILE_N = 12

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}


def week_slots(e):
    out = []
    for t in e.get("tickets", []):
        if t.get("soldout") or t.get("saleEnded"):
            continue
        sd = t.get("startDate") or ""
        if not (FROM <= sd <= TO):
            continue
        if not re.search(r"\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売", t.get("type") or ""):
            continue
        out.append(t)
    return out


buf = ["=== 今週のピックアップ 素材（対象 %s〜%s）===" % (FROM, TO), ""]
buf.append("【主役5組】")
for i in MAIN:
    e = by_id.get(i)
    if not e:
        buf.append("  id=%s が見つからない" % i); continue
    ss = week_slots(e)
    buf.append("")
    buf.append("■ id%s %s  [%s]" % (i, e.get("name"), e.get("genre")))
    buf.append("   公演期間: %s" % e.get("dateLabel"))
    buf.append("   会場    : %s" % e.get("venue"))
    buf.append("   県      : %s" % e.get("prefecture"))
    buf.append("   ぴあ    : %s" % ((e.get("links") or {}).get("pia") or ""))
    buf.append("   今週の発売枠 %d本:" % len(ss))
    for t in ss:
        buf.append("     - %s ／ 受付終了 %s" % (t.get("type"), t.get("date")))
    other = [t for t in e.get("tickets", []) if t not in ss]
    if other:
        buf.append("   （今週以外の枠 %d本＝記事には出さないが状況把握用）" % len(other))
        for t in other[:6]:
            buf.append("     ・%s ／ 〜%s" % (t.get("type"), t.get("date")))

# 名前タイル＝主役以外で今週の発売枠が多い順
rows = []
for e in events:
    if e.get("id") in MAIN or e.get("genre") == "new":
        continue
    ss = week_slots(e)
    if ss:
        rows.append((len(ss), e, ss))
rows.sort(key=lambda r: (-r[0], r[1].get("date") or ""))

buf.append("")
buf.append("【名前タイル候補（上位%d組）】" % TILE_N)
for n, (c, e, ss) in enumerate(rows[:TILE_N], 1):
    d = sorted(set(t.get("startDate") for t in ss))
    tm = sorted(set(re.search(r"(\d{1,2}:\d{2})発売", t.get("type")).group(1)
                    for t in ss if re.search(r"(\d{1,2}:\d{2})発売", t.get("type"))))
    buf.append("%2d. %s [%s] 枠%d / 発売%s %s / %s" % (
        n, e.get("name"), e.get("genre"), c, ",".join(d), ",".join(tm), e.get("prefecture")))

buf.append("")
buf.append("【この週ぜんぶの数】")
allrows = [r for r in rows] + [(len(week_slots(by_id[i])), by_id[i], []) for i in MAIN if by_id.get(i)]
buf.append("  アーティスト %d組 / 発売枠 %d本" % (len(allrows), sum(r[0] for r in allrows)))

io.open("tmp/pickup_material_0907.txt", "w", encoding="utf-8").write("\n".join(buf))
print("MAIN=%d  TILE=%d  WEEK_ARTISTS=%d  WEEK_SLOTS=%d" % (
    len(MAIN), min(TILE_N, len(rows)), len(allrows), sum(r[0] for r in allrows)))
print("WROTE tmp/pickup_material_0907.txt")
