# -*- coding: utf-8 -*-
"""保留にしていたキーウ・クラシック・バレエ2件（受付中・演劇の組み立て）を、942「2026 全国ツアー」に畳む仕分けファイルを作る（読むだけ）。
確かめたこと（2026-09-14 朝）＝942 の登録枠に 千葉11/15 も 香川12/26 も無い＝二重にならない。
  8580「白鳥の湖（全2幕）」千葉 市川市文化会館 11/15 → 942
  8581「ロミオとジュリエット-全幕-」香川 レクザムホール 12/26 → 942（4638 は愛知11/14だけの別エントリ。ツアーの続きは942へ）
使い方: python tmp/prep_kiev_0914.py
出力: tmp/merge_kiev_built_0914.json ＋ tmp/merge_kiev_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk02_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk02_0914.json', encoding='utf-8'))}
MERGE = {8580: 942, 8581: 942}
json.dump([built[i] for i in MERGE], io.open('tmp/merge_kiev_built_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in MERGE.items()],
          io.open('tmp/merge_kiev_cands_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('キーウ %d件を 942 に畳む準備ができた' % len(MERGE))
