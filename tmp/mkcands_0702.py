# -*- coding: utf-8 -*-
"""7/2 発売前新着: 演劇(02)+クラシック(07)のharvest結果から真の発売前(rlsdate有)を
url重複除去して抽出し、rlsdate昇順(発売日が近い＝発売前ファースト)で候補JSONを組む。
出力: tmp/cands_0702.json = [{"newid":int,"artist":str,"urls":[url]}, ...]
採番は id 1812 から。TARGET件数だけ拾う(build段でskip出る想定でバッファ多め)。"""
import json, io, sys, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

START_ID = 1812
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 58   # バッファ込み

def load(path):
    try:
        return json.load(open(path, encoding='utf-8'))['new']
    except FileNotFoundError:
        return []

pool = []
for path, tag in [('tmp/presale_02_0702.json', '演劇'), ('tmp/presale_07_0702.json', 'クラシック')]:
    for x in load(path):
        x['_src'] = tag
        pool.append(x)

# url重複除去
seen = set(); uniq = []
for x in pool:
    if x['url'] in seen: continue
    seen.add(x['url']); uniq.append(x)

# 真の発売前のみ(rlsdate有・TODAY除く=今日発売はreconcile不可なので今回外す)
pre = [x for x in uniq if x['rlsdate'] and x['rlsdate'] != 'TODAY']

# 既存DBのeventCd集合(取得済みと衝突しないよう二重チェック)
idx = open('index.html', encoding='utf-8').read()
ex_cd = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
    return m.group(1) if m else None
pre = [x for x in pre if cd_of(x['url']) not in ex_cd]

# rlsdate昇順(発売日が近い順=発売前ファースト)
def keyd(x):
    y, m, d = map(int, x['rlsdate'].split('/'))
    return (y, m, d)
pre.sort(key=keyd)

# 同一アーティスト集中を抑える(定期演奏会シリーズ等が新着プールを埋め尽くさないよう)。
# 粗いキー=NFKC正規化先頭6文字。1アーティスト最大CAP件までで多様性確保。
CAP = 3
def akey(x):
    s = unicodedata.normalize('NFKC', x['artist'])
    s = re.sub(r'[\s　・／/（）()【】「」]', '', s)
    return s[:6]
cnt = {}
picked = []
for x in pre:
    k = akey(x)
    if cnt.get(k, 0) >= CAP:
        continue
    cnt[k] = cnt.get(k, 0) + 1
    picked.append(x)
    if len(picked) >= TARGET:
        break
cands = []
nid = START_ID
for x in picked:
    cands.append({'newid': nid, 'artist': x['artist'], 'urls': [x['url']],
                  '_src': x['_src'], '_rls': x['rlsdate'], '_pref': x['pref']})
    nid += 1

json.dump(cands, open('tmp/cands_0702.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print('候補', len(cands), 'id', START_ID, '..', nid - 1, '| 内訳', dict(Counter(c['_src'] for c in cands)))
for c in cands:
    print(' ', c['newid'], c['_rls'], c['_src'], '|', c['artist'][:32], '|', c['_pref'])
