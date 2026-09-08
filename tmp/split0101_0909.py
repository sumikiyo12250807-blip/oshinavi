# -*- coding: utf-8 -*-
"""部分一致18件を中身で仕分けた結果、本物の統合4件を投入から外す。

統合行き（同じ興行の券種違い／同じツアーの別会場）
  7627 New Acoustic Camp 2026<サウナエリア>          → 既存 id6481（公演日も9/20で同じ）
  7628 New Acoustic Camp 2026<宝川温泉ツアー ほか>     → 既存 id6481
  7632 THEカルテットの昭和歌謡コンサート（蓮田10月公演）    → 既存 id2735（同じツアー）
  7633 THEカルテットの昭和歌謡コンサート（朝霞11月公演）    → 既存 id2735
残り14件は別物と判断して投入する
  ・「サーカス」はグループ名と一般語の衝突（メランコリックサーカス等とは別）
  ・My Little Lover／鈴木雅之／水森かおり／渡辺貞夫／渡辺美里／東儀秀樹／大月みやこ／
    中西圭三／TAGRIGHT ＝同じ人の別公演。既存も1公演1エントリで運用している
"""
import io, json, sys
sys.stdout.reconfigure(encoding="utf-8")
MERGE = {7627: 6481, 7628: 6481, 7632: 2735, 7633: 2735}
d = json.load(io.open("tmp/built0101_0909.json", encoding="utf-8"))
keep = [x for x in d if x["id"] not in MERGE]
mrg = [x for x in d if x["id"] in MERGE]
json.dump(keep, io.open("tmp/built0101_keep_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(mrg, io.open("tmp/built0101_merge_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("投入 %d件 / 統合行き %d件" % (len(keep), len(mrg)))
for x in mrg:
    print("   id%d %s → 既存 id%d" % (x["id"], x["name"][:44], MERGE[x["id"]]))
