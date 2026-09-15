# -*- coding: utf-8 -*-
"""総ざらい1本めの組み上がりを「既存に畳む」と「新着に入れる」に分ける（読むだけ・2026-09-15夜）。
  畳む＝built_merge.json の7件（target は cand_merge.json）
      ＋ TSUKEMEN 長崎 R9年2/6（10721）・福岡 R9年2/7（10722）→ 8404 TSUKEMEN（R9年2/21〜2/23 岩手・宮城）＝同じ2027年のツアー
  新着＝built_new.json の残り
使い方: python tmp/x0916/prep_fold1.py
出力: tmp/x0916/fold1_built.json ＋ tmp/x0916/fold1_cands.json（merge_with_urls_0912.py 用）／ tmp/x0916/inject1.json（inject_built.py 用）
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
TO_FOLD = {10721: 8404, 10722: 8404}
bm = json.load(io.open('tmp/x0916/built_merge.json', encoding='utf-8'))
bn = json.load(io.open('tmp/x0916/built_new.json', encoding='utf-8'))
cm = json.load(io.open('tmp/x0916/cand_merge.json', encoding='utf-8'))
cn = {c['newid']: c for c in json.load(io.open('tmp/x0916/cand_new.json', encoding='utf-8'))}
fold_b = list(bm) + [b for b in bn if b['id'] in TO_FOLD]
fold_c = list(cm) + [dict(cn[i], target=t) for i, t in TO_FOLD.items()]
inj = [b for b in bn if b['id'] not in TO_FOLD]
assert {b['id'] for b in fold_b} == {c['newid'] for c in fold_c}, '組み上がりと候補の番号が合わない'
json.dump(fold_b, io.open('tmp/x0916/fold1_built.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(fold_c, io.open('tmp/x0916/fold1_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(inj, io.open('tmp/x0916/inject1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for c in fold_c:
    print('畳む %s → id%s' % (c['artist'][:30], c['target']))
print('畳む %d ／ 新着 %d（%s）' % (len(fold_b), len(inj), ' '.join(str(b['id']) for b in inj)))
