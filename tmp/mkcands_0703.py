# -*- coding: utf-8 -*-
"""7/3 発売前新着: 演劇(02)+クラシック(07)harvestから真の発売前(rlsdate有・非TODAY)を
url重複除去して抽出し、rlsdate昇順(発売前ファースト)で候補JSONを組む。採番 id 1870〜。
同一アーティストCAP=3で多様性確保。出力: tmp/cands_0703.json"""
import json, io, sys, re, unicodedata
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

START_ID = 1870
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 58

def load(path):
    try:
        return json.load(open(path, encoding='utf-8'))['new']
    except FileNotFoundError:
        return []

pool = []
for path, tag in [('tmp/presale_02_0703.json', '演劇'), ('tmp/presale_07_0703.json', 'クラシック')]:
    for x in load(path):
        x['_src'] = tag
        pool.append(x)

# url重複除去(overrunの再取得ダブりを潰す)
seen = set(); uniq = []
for x in pool:
    if x['url'] in seen: continue
    seen.add(x['url']); uniq.append(x)

# 真の発売前のみ(rlsdate有・TODAY除外=今日発売はreconcile不可)
pre = [x for x in uniq if x['rlsdate'] and x['rlsdate'] != 'TODAY']

# 既存DBのeventCd集合で二重チェック
idx = open('index.html', encoding='utf-8').read()
ex_cd = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
    return m.group(1) if m else None
pre = [x for x in pre if cd_of(x['url']) not in ex_cd]

# rlsdate昇順(発売前ファースト)
def keyd(x):
    y, m, d = map(int, x['rlsdate'].split('/'))
    return (y, m, d)
pre.sort(key=keyd)

# 同一アーティストCAP
CAP = 3
def akey(x):
    s = unicodedata.normalize('NFKC', x['artist'])
    s = re.sub(r'[\s　・／/（）()【】「」]', '', s)
    return s[:6]
cnt = {}; picked = []
for x in pre:
    k = akey(x)
    if cnt.get(k, 0) >= CAP: continue
    cnt[k] = cnt.get(k, 0) + 1
    picked.append(x)
    if len(picked) >= TARGET: break

cands = []; nid = START_ID
for x in picked:
    cands.append({'newid': nid, 'artist': x['artist'], 'urls': [x['url']],
                  '_src': x['_src'], '_rls': x['rlsdate'], '_pref': x['pref']})
    nid += 1

json.dump(cands, open('tmp/cands_0703.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('候補', len(cands), 'id', START_ID, '..', nid - 1, '| 内訳', dict(Counter(c['_src'] for c in cands)))
print('発売前プール総数(url dedup後・非TODAY・未掲載):', len(pre))
for c in cands:
    print(' ', c['newid'], c['_rls'], c['_src'], '|', c['artist'][:32], '|', c['_pref'])
