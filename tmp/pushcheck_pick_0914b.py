# -*- coding: utf-8 -*-
"""昼のpushの前に、独立の読み直しをもう一段厚くするための対象選び（読むだけ・2026-09-14）。
  U＝照合で「未照合（同じ締切の枠が2つ以上で対を決められない）」になる枠を持つ新着エントリ（まだ読み直していない分）
  R＝まだ読み直していない新着から、ジャンルの大きさに比例して抜き取る（乱数の種は固定＝やり直しても同じ）
出力: tmp/pushcheck_W_0914.txt（U）／tmp/pushcheck_X_0914.txt（R）＝「id<TAB>公演名<TAB>URL…」の行
使い方: python tmp/pushcheck_pick_0914b.py [Rの件数=40]
"""
import glob
import io
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
NR = int(sys.argv[1]) if len(sys.argv) > 1 else 40
TODAY = '2026-09-14'
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
new = {e['id']: e for e in ev if e.get('genre') == 'new'}

seen = set()
for p in glob.glob(os.path.join(SP, '*result*.json')):
    try:
        rows = json.load(io.open(p, encoding='utf-8'))
    except Exception:
        continue
    if isinstance(rows, list):
        seen |= {r.get('id') for r in rows if isinstance(r, dict)}


def visible(t):
    if t.get('soldout'):
        return False
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in us:
            us.append(u)
    return us


U = []
for i, e in sorted(new.items()):
    if i in seen:
        continue
    ds = [t.get('date') for t in e.get('tickets') or [] if visible(t) and 'pia.jp' in ((t.get('url') or (e.get('links') or {}).get('pia') or ''))]
    if len(ds) != len(set(ds)):
        U.append(i)

rest = [i for i in sorted(new) if i not in seen and i not in U]
by_g = {}
for i in rest:
    by_g.setdefault(new[i].get('_genre') or '?', []).append(i)
rnd = random.Random(914)
R = []
tot = len(rest)
for g, ids in sorted(by_g.items(), key=lambda x: -len(x[1])):
    k = max(1, round(NR * len(ids) / tot)) if len(ids) >= 5 else 0
    R += rnd.sample(ids, min(k, len(ids)))
R = sorted(R)[:NR + 5]


def dump(path, ids):
    with io.open(path, 'w', encoding='utf-8') as f:
        for i in ids:
            e = new[i]
            f.write('%s\t%s\t%s\n' % (i, (e.get('name') or '')[:50], '\t'.join(pia_urls(e))))


dump('tmp/pushcheck_W_0914.txt', U)
dump('tmp/pushcheck_X_0914.txt', R)
print('読み直し済み %d件 ／ U（未照合の枠を持つ・未読）%d件 ／ R（ジャンル比例の抜き取り）%d件' % (len(seen & set(new)), len(U), len(R)))
gs = {}
for i in R:
    g = new[i].get('_genre') or '?'
    gs[g] = gs.get(g, 0) + 1
print('R の内訳: ' + ' '.join('%s%d' % (g, n) for g, n in sorted(gs.items(), key=lambda x: -x[1])))
