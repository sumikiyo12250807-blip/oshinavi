# -*- coding: utf-8 -*-
"""受付中・音楽の組み立て14件（tmp/built_uk01_0914.json）を「既存に畳む」「新規投入」に分ける（読むだけ・2026-09-14）。
split_built_0914.py の結果を1件ずつ見て決めた:
  畳む（完全一致1件・既存ツアーの会期の中かすぐ続き）＝IDLM×4→7424／Arakezuri→2660／因幡晃→617／イルカ→620／
      ウルトラ寿司→7191／おいしくるメロンパン→2202
  畳む（完全一致が2件＝9/13から保留していた要確認のうち、行き先が決まった分）
      杏里 広島11/5 → 612「杏里 2026」ツアー（7338 は北海道だけの別公演）
      五木ひろし 東京10/3・神奈川10/6 → 1383「五木ひろし」（6983 はジャパネットのトーク&ライブ＝別の催し）
      宇崎竜童 石川9/27 → 627「宇崎竜童 2026」（7101 は2027年3月の静岡）
  新規＝伊波杏樹 東京（既存 5811 大阪・5842 愛知 が会場ごとの別エントリ＝同じ形で）
使い方: python tmp/prep_uk01_0914.py
出力: tmp/inject_uk01_0914.json ／ tmp/merge_uk01_built_0914.json ＋ tmp/merge_uk01_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk01_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk01_0914.json', encoding='utf-8'))}

MERGE = {
    8433: 7424, 8434: 7424, 8435: 7424, 8436: 7424,  # I Don't Like Mondays.
    8445: 2660,  # Arakezuri
    8459: 617,   # 因幡晃
    8463: 620,   # イルカ
    8468: 7191,  # ウルトラ寿司ふぁいやー
    8477: 2202,  # おいしくるメロンパン
    8453: 612,   # 杏里
    8457: 1383, 8458: 1383,  # 五木ひろし
    8465: 627,   # 宇崎竜童
}
NEW = {8460}  # 伊波杏樹 東京

left = set(built) - set(MERGE) - NEW
assert not left, '行き先の決まっていない組み立てがある %s' % sorted(left)
inject = [built[i] for i in sorted(NEW)]
mb = [built[i] for i in MERGE]
mc = [dict(cands[i], target=t) for i, t in MERGE.items()]
json.dump(inject, io.open('tmp/inject_uk01_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mb, io.open('tmp/merge_uk01_built_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/merge_uk01_cands_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規投入 %d件 / 既存に畳む %d件（組み立て %d）' % (len(inject), len(mb), len(built)))
