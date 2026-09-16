# -*- coding: utf-8 -*-
"""発売前スイープの組み上がり（tmp/built_presale_0915.json）の残り＝「追加で畳む」と「新規」を分ける（読むだけ・2026-09-15 昼）。
名前が完全一致1件の13件は merge_with_urls_0912.py で畳み済み。ここはその残り。
決めたこと（split_built_ps0915.txt・partial_compare_ps0915.txt・multi_match_plan_ps0915.txt を見て）:
  部分一致5件
    入れない（二重）＝10473『わたしの知らない子どもたち』福岡（7944 と枠が同じ）
    新規＝10454 牧阿佐美バレヱ団「眠れる森の美女」東京（7487 は大阪の別公演）／10478 カネヨリマサル／reGretGirl（学祭の2マン）／
          10489 上野耕平 東京3/14（4431 は札幌の3人の公演）／10496 東京21世紀管弦楽団「第九」12/5（1公演1エントリの形）
  複数一致3件
    畳む＝10432 syrup16g 長野11/26 → 5526（会期の中）／10465 新日本プロレス 茨城10/27 → 5755（会期の中）
    新規＝10462 OZアカデミー 大阪12/6（既存は1大会1エントリの形）
使い方: python tmp/prep_ps0915.py
出力: tmp/merge2_ps_built_0915.json ＋ tmp/merge2_ps_cands_0915.json ／ tmp/inject_ps_0915.json
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_presale_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_presale_0915.json', encoding='utf-8'))}
merged_already = {c['newid'] for c in json.load(io.open('tmp/merge_cands_ps0915.json', encoding='utf-8'))}
split = io.open('tmp/split_built_ps0915.txt', encoding='utf-8').read()

SKIP_DUP = {10473}
MERGE = {10432: 5526, 10465: 5755}
NEW_EXTRA = {10462}
pure_new = {int(m.group(1)) for m in re.finditer(r'^新規\s+new(\d+)', split, re.M)}
partial = {int(m.group(1)) for m in re.finditer(r'^👀部分 new(\d+)', split, re.M)}
NEW = (pure_new | partial | NEW_EXTRA) - SKIP_DUP - set(MERGE)
decided = merged_already | SKIP_DUP | set(MERGE) | NEW
left = set(built) - decided
assert not left, '行き先の決まっていない組み上がりがある %s' % sorted(left)

json.dump([built[i] for i in sorted(MERGE)], io.open('tmp/merge2_ps_built_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in sorted(MERGE.items())], io.open('tmp/merge2_ps_cands_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([built[i] for i in sorted(NEW)], io.open('tmp/inject_ps_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/inject_ps_ids_0915.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(NEW)))
print('組み上がり %d ＝ 畳み済み %d ／ 追加で畳む %d ／ 新規 %d ／ 二重で入れない %d' % (
    len(built), len(merged_already), len(MERGE), len(NEW), len(SKIP_DUP)))
