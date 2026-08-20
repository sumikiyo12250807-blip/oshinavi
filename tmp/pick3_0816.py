# -*- coding: utf-8 -*-
"""2026-08-16 夜の新着50件の候補づくり（2バッチ目）。
朝のスイープで拾った受付中(音楽・146件)のうち未使用分から組む。
発売前(rlsIn=03/04)は朝に取り切ったので在庫なし＝受付中で穴埋めする運用（feedback_presale_first_harvest）。
締切が近い子はbuild後に落とすので、多めに候補化する。
"""
import json, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

WANT = 74           # build後に締切で落とすので多めに
src = open('index.html', 'rb').read().decode('utf-8')
have = set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', src))

def cd(u):
    m = re.search(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', u or '')
    return m.group(1) if m else ''

def load(path):
    rows = json.load(open(path, encoding='utf-8'))['new']
    order, groups = [], {}
    for r in rows:
        a = r['artist']
        if a not in groups:
            groups[a] = []; order.append(a)
        groups[a].append(r)
    return [{'artist': a, 'urls': [x['url'] for x in groups[a]]} for a in order]

seen, picked, skipped = set(), [], 0
for c in load('tmp/onsale_music_0816.json'):
    if len(picked) >= WANT:
        break
    codes = [cd(u) for u in c['urls']]
    if any(x and (x in have or x in seen) for x in codes):
        skipped += 1; continue
    seen.update(x for x in codes if x)
    picked.append({'newid': 0, 'artist': c['artist'], 'urls': c['urls'], '_grp': 'music_onsale'})

start = 4376
for i, c in enumerate(picked):
    c['newid'] = start + i

json.dump(picked, open('tmp/cand_pick2_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("候補 %d件（id %d〜%d）／既出スキップ %d" % (len(picked), picked[0]['newid'], picked[-1]['newid'], skipped))
for c in picked[:12]:
    print("  %d %s (%d本)" % (c['newid'], c['artist'][:40], len(c['urls'])))
