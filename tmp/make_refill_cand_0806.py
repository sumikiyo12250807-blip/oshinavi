# -*- coding: utf-8 -*-
"""阪神統合で空いた15枠の補充候補を作る（音楽優先・ツアーはURLをまとめて1エントリ）。

選定の考え方（[[feedback_harvest_countdown_first]]／[[feedback_capture_all_not_select]]）:
  ①「発売まで4日以上」を先に（今日の在庫では中田カウス8/18・さやか8/15の2組だけ）
  ②残りは音楽(01)→演劇(02)の順。今朝のcand_newは音楽5/演劇4しか入っていないので音楽を厚くする
  ③同じ公演・同じシリーズが別ページになっているものはURLをまとめて1エントリにする
"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

E = "https://t.pia.jp/pia/event/event.do?eventCd=%s"
B = "https://t.pia.jp/pia/event/event.do?eventBundleCd=%s"

ROWS = [
    # (下書き元ジャンル, 名前メモ, [URL...])
    ("engeki", "中田カウス漫才のDENDO 全国ツアーin川越町", [E % "2621795"]),
    ("engeki", "さやかミニ落語会 2026年度 第4回〜第6回", [E % "2623657", E % "2623659"]),
    ("music", "HY", [E % "2620975", E % "2631489", E % "2607685", E % "2621396",
                     E % "2621384", E % "2621417", E % "2631488"]),
    ("music", "Kobe Calling 2026", [E % "2631003", E % "2630990"]),
    ("music", "SUSHIBOYS", [E % "2628372", E % "2631503"]),
    ("music", "眞名子新", [E % "2625519", E % "2620883"]),
    ("music", "THEカルテットの昭和歌謡コンサート", [E % "2629199", E % "2630041"]),
    ("music", "岡咲美保", [B % "b2669828"]),
    ("music", "えんがわ音楽祭 〜水の音コンサート〜メインコンサート", [E % "2630202"]),
    ("music", "Tribute for OSCAR PEATERSON", [E % "2628841"]),
    ("music", "はる コンサート 2026", [E % "2626682"]),
    ("music", "HAMMER BALL 2026", [E % "2630614"]),
    ("music", "パンタレイ", [E % "2621950"]),
    ("music", "PM AGENCY 40th ANNIVERSARY LIVE スーパー大感謝祭", [B % "b2668938"]),
    ("music", "Yoshi 独演会 2026", [E % "2631104"]),
]

START = 3859
out = []
for i, (g, name, urls) in enumerate(ROWS):
    out.append({"newid": START + i, "artist": name, "urls": urls, "_srcgenre": g})
json.dump(out, open("tmp/cand_refill_0806.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("補充候補 %d件 / URL %d本 → tmp/cand_refill_0806.json (id %d..%d)" % (
    len(out), sum(len(r[2]) for r in ROWS), START, START + len(out) - 1))
