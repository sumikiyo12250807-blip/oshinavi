# -*- coding: utf-8 -*-
"""受付中・映画（22件）とアート（28件）の組み立てを「既存に畳む」「新規投入」に分ける（読むだけ・2026-09-14）。
split_built_0914.py の結果を見て決めた:
  映画＝22件とも新規（9047 DEEN の Blu-ray&DVD 発売記念イベントは、既存 4169 DEEN のコンサートとは別の催し）
  アート＝9067 ゴールドマン コレクション 河鍋暁斎の世界 → 5487 に畳む／残り27件は新規
中止・延期・販売を終了致しましたを弾く直しの後に組んだ分。
使い方: python tmp/prep_uk0405_0914.py
出力: tmp/inject_uk0405_0914.json ／ tmp/merge_uk0405_built_0914.json ＋ tmp/merge_uk0405_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built, cands = {}, {}
for lg in ('04', '05'):
    built.update({b['id']: b for b in json.load(io.open('tmp/built_uk%s_0914.json' % lg, encoding='utf-8'))})
    cands.update({c['newid']: c for c in json.load(io.open('tmp/cands_uk%s_0914.json' % lg, encoding='utf-8'))})
MERGE = {9067: 5487}
missing = [i for i in MERGE if i not in built]
assert not missing, '組み立てに無い id を指している %s' % missing
new_ids = sorted(set(built) - set(MERGE))
json.dump([built[i] for i in new_ids], io.open('tmp/inject_uk0405_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([built[i] for i in MERGE], io.open('tmp/merge_uk0405_built_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in MERGE.items()],
          io.open('tmp/merge_uk0405_cands_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て %d件 ＝ 新規投入 %d / 既存に畳む %d' % (len(built), len(new_ids), len(MERGE)))
print('新規のid範囲 %s〜%s' % (new_ids[0], new_ids[-1]))
