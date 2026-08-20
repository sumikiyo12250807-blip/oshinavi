# -*- coding: utf-8 -*-
"""2026-08-16 新着50件の候補づくり（第2版）。
発売前(rlsIn=03/04)を全部使っても38件しか無かったので、受付中(rlsStatus=0201)の音楽で穴埋めする。
優先順＝①音楽 ②演劇/クラシック ③その他（feedback_harvest_genre_priority）。
受付中は「締切がすぐ来る子」を載せない約束なので、少し多めに候補化してbuild後に締切で切る。
"""
import json, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

WANT = 50
ONSALE_EXTRA = 24          # 受付中は多めに候補化して、build後に締切で落とす
src = open('index.html', 'rb').read().decode('utf-8')
have = set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', src))

def cd(u):
    m = re.search(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', u or '')
    return m.group(1) if m else ''

cand03 = json.load(open('tmp/cand_0816.json', encoding='utf-8'))
g03 = {'music': [], 'engeki': [], 'classic': [], 'other': []}
for c in cand03:
    k = c.get('_srcgenre')
    g03[k if k in ('music', 'engeki', 'classic') else 'other'].append(c)

def load(path):
    rows = json.load(open(path, encoding='utf-8'))['new']
    order, groups = [], {}
    for r in rows:
        a = r['artist']
        if a not in groups:
            groups[a] = []; order.append(a)
        groups[a].append(r)
    return [{'artist': a, 'urls': [x['url'] for x in groups[a]]} for a in order]

seen, picked, skipped = set(), [], []
def take(items, tag, limit=None):
    n = 0
    for c in items:
        if len(picked) >= WANT + ONSALE_EXTRA or (limit and n >= limit):
            return
        codes = [cd(u) for u in c['urls']]
        if any(x and (x in have or x in seen) for x in codes):
            skipped.append((tag, c['artist'])); continue
        seen.update(x for x in codes if x)
        picked.append({'newid': 0, 'artist': c['artist'], 'urls': c['urls'], '_grp': tag})
        n += 1

# ① 音楽（発売前：遠い発売日のrlsIn=04が先）
take(load('tmp/presale_music04_0816.json'), 'music04')
take(g03['music'], 'music03')
# ② 演劇・クラシック（発売前）
take(load('tmp/presale_engeki04_0816.json'), 'engeki04')
take(load('tmp/presale_classic04_0816.json'), 'classic04')
take(g03['engeki'], 'engeki03')
take(g03['classic'], 'classic03')
# ③ その他（発売前）
take(load('tmp/presale_event04_0816.json'), 'event04')
take(load('tmp/presale_movie04_0816.json'), 'movie04')
take(g03['other'], 'other03')
presale_n = len(picked)
# ④ 穴埋め＝受付中の音楽（締切はbuild後に確認して切る）
take(load('tmp/onsale_music_0816.json'), 'music_onsale')

start = 4326
for i, c in enumerate(picked):
    c['newid'] = start + i

json.dump(picked, open('tmp/cand_pick_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("候補 %d件（うち発売前 %d件・受付中の穴埋め %d件）id %d〜%d" % (
    len(picked), presale_n, len(picked) - presale_n, picked[0]['newid'], picked[-1]['newid']))
print("内訳:", dict(Counter(c['_grp'] for c in picked)))
print("重複スキップ:", len(skipped))
for c in picked[presale_n:]:
    print("  穴埋め %d %s (%d本)" % (c['newid'], c['artist'][:40], len(c['urls'])))
