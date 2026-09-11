# -*- coding: utf-8 -*-
"""受付中のビルド結果（tmp/built_uk_0912.json・69件）を「新規で入れる／既存に足す／保留」に分ける（読むだけ・tmpに書く）。
判断は 2026-09-12 朝にあたしが部分一致21件を1件ずつ見て決めた（tmp/dupcheck_loose_built_0823.txt）。
  足す＝同じアーティストの別の日・別会場（ツアーは1エントリ＝feedback_tour_consolidate）
  新規＝名前が似ているだけの別物（2マン・対バン企画・別グループ）
  保留＝8178 ボロフェスタ2026（既存6251は「METRO券」だけのエントリ。まとめ方を決め切れない）
🚨足す分は1件ずつ別の仮idのまま足す先(target)を持たせる＝同じ相手に2件来てもURLを取り違えない
出力: tmp/inject_uk_0912.json（新規）／ tmp/built_mergeUK_0912.json ＋ tmp/cand_mergeUK_0912.json（足す）／
      tmp/built_mergeUK_check_0912.json（重なりチェック用に id を足す先に置き換えたもの）
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
MERGE = {8161: 7637, 8162: 8030, 8227: 8030, 8193: 8115, 8200: 7684, 8254: 7684, 8209: 7973,
         8216: 8005, 8221: 8013, 8223: 8015, 8233: 7696, 8248: 7698, 8177: 554}
HOLD = {8178}

built = json.load(io.open('tmp/built_uk_0912.json', encoding='utf-8-sig'))
ids = {b['id'] for b in built}
missing = (set(MERGE) | HOLD) - ids
assert not missing, 'ビルド結果に無いid: %s' % sorted(missing)

inject, mb, mc, chk = [], [], [], []
for b in built:
    if b['id'] in HOLD:
        continue
    if b['id'] in MERGE:
        url = (b.get('links') or {}).get('pia')
        mb.append(b)
        mc.append({'newid': b['id'], 'target': MERGE[b['id']], 'artist': b.get('artist'), 'urls': [url]})
        c = json.loads(json.dumps(b))
        c['id'] = MERGE[b['id']]
        chk.append(c)
        continue
    inject.append(b)

for p, d in (('tmp/inject_uk_0912.json', inject), ('tmp/built_mergeUK_0912.json', mb),
             ('tmp/cand_mergeUK_0912.json', mc), ('tmp/built_mergeUK_check_0912.json', chk)):
    json.dump(d, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('受付中 %d件 ＝ 新規 %d ／ 既存に足す %d ／ 保留 %d' % (len(built), len(inject), len(mb), len(HOLD)))
print('新規のid: %s' % ','.join(str(b['id']) for b in inject))
