# -*- coding: utf-8 -*-
"""7.5（明日〜3日後発売のぴあ一覧との突き合わせ）で見つかった分の組み上がり（tmp/x0916/built_misc_0915.json）を分ける（読むだけ・2026-09-15夜）。
  90021 第54回 関西マーチングコンテスト → 7156 に畳む（merge_with_urls）
  90022 荒牧陽子&ビューティーこくぶ クリスマスディナーショー → 新規（新着へ）
  90023 Piano Dream Land 2026 → 新規（新着へ）
新規の id は、index.html の最大 id と last_batch の最大 id_to と今日の候補ファイルの最大 newid の次から振る（仮の 9002x のまま入れない）。
使い方: python tmp/x0916/prep_misc.py
出力: tmp/x0916/merge_misc_built.json ＋ tmp/x0916/merge_misc_cands.json ／ tmp/x0916/inject_misc.json
"""
import glob
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/x0916/built_misc_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/x0916/cand_misc_0915.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
ev_ids = [e['id'] for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))]
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
cand_max = 0
for p in glob.glob('tmp/cands_*_0915.json'):
    try:
        cand_max = max([cand_max] + [c.get('newid') or 0 for c in json.load(io.open(p, encoding='utf-8'))])
    except Exception:
        pass
nid = max(ev_ids + [b.get('id_to') or 0 for b in lb] + [cand_max])

json.dump([built[90021]], io.open('tmp/x0916/merge_misc_built.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[90021], target=7156)], io.open('tmp/x0916/merge_misc_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
inject = []
for old in (90022, 90023):
    nid += 1
    b = dict(built[old])
    b['id'] = nid
    inject.append(b)
    print('  新規 %s → id%s %s' % (old, nid, b.get('name')))
json.dump(inject, io.open('tmp/x0916/inject_misc.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('畳む1（→7156）／新規 %d件 → tmp/x0916/inject_misc.json' % len(inject))
