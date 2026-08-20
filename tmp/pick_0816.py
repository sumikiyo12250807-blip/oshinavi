# -*- coding: utf-8 -*-
"""2026-08-16 朝の新着50件の候補づくり。
優先順（feedback_harvest_genre_priority）＝①音楽 ②演劇/クラシック/お笑い ③その他。
在庫＝rlsIn=03スイープ(tmp/cand_0816.json・harvest_newが選定済み)＋rlsIn=04スイープ(music/engeki/classic)。
rlsIn=04 は「発売が30日より先」＝カウントダウンの価値が高いのでグループ内で先頭に置く。
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

WANT = 50
src = open('index.html', 'rb').read().decode('utf-8')
have = set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', src))

def cd(u):
    m = re.search(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', u or '')
    return m.group(1) if m else ''

# ---- rlsIn=03 の既選定（グループ別に分解）----
cand03 = json.load(open('tmp/cand_0816.json', encoding='utf-8'))
g03 = {'music': [], 'engeki': [], 'classic': [], 'other': []}
for c in cand03:
    k = c.get('_srcgenre')
    g03[k if k in ('music', 'engeki', 'classic') else 'other'].append(c)

# ---- rlsIn=04（アーティスト単位でまとめる）----
def load04(path):
    rows = json.load(open(path, encoding='utf-8'))['new']
    order, groups = [], {}
    for r in rows:
        a = r['artist']
        if a not in groups:
            groups[a] = []; order.append(a)
        groups[a].append(r)
    return [{'artist': a, 'urls': [x['url'] for x in groups[a]]} for a in order]

g04 = {
    'music': load04('tmp/presale_music04_0816.json'),
    'engeki': load04('tmp/presale_engeki04_0816.json'),
    'classic': load04('tmp/presale_classic04_0816.json'),
}

seen, picked, skipped = set(), [], []
def take(items, tag):
    for c in items:
        if len(picked) >= WANT:
            return
        urls = c['urls']
        codes = [cd(u) for u in urls]
        if any(x and (x in have or x in seen) for x in codes):
            skipped.append((tag, c['artist'])); continue
        seen.update(x for x in codes if x)
        picked.append({'newid': 0, 'artist': c['artist'], 'urls': urls, '_grp': tag})

# ① 音楽（発売が遠いrlsIn=04を先に）
take(g04['music'], 'music04'); take(g03['music'], 'music03')
# ② 演劇・クラシック
take(g04['engeki'], 'engeki04'); take(g04['classic'], 'classic04')
take(g03['engeki'], 'engeki03'); take(g03['classic'], 'classic03')
# ③ その他（イベント/アートは最後）
take(g03['other'], 'other03')

start = 4326
for i, c in enumerate(picked):
    c['newid'] = start + i

json.dump(picked, open('tmp/cand_pick_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print("選定 %d件 (id %d〜%d)" % (len(picked), picked[0]['newid'], picked[-1]['newid']))
print("内訳:", dict(Counter(c['_grp'] for c in picked)))
print("重複スキップ:", len(skipped), skipped[:6])
for c in picked:
    print("  %d [%s] %s (%d本)" % (c['newid'], c['_grp'], c['artist'][:40], len(c['urls'])))
