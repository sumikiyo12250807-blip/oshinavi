# -*- coding: utf-8 -*-
"""読み直しの pia_genre と登録の _piaSub を「分類名」で突き合わせる（読むだけ・2026-09-16）。
エージェントの pia_genre は「パンくず:… ／ 分類:… ／ ntSgenreCd:…」の形で、まとめページは番号だけのことがある。
番号→分類名の対応は、結果の中で両方そろっている行から作る（推測で埋めない＝作れない番号は「判定できない」）。
使い方: python tmp/compare_genre_0916.py
"""
import collections
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
from build_pia_entries import PIA_GENRE_CD  # noqa: E402
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


rows = []
for p in sorted(glob.glob(os.path.join(SP, 'recheck_*_result.json'))):
    rows += json.load(io.open(p, encoding='utf-8'))


def parts(g):
    g = g or ''
    cls = re.search(r'分類[:：]\s*([^／/]+?)\s*(?:／|$)', g)
    code = re.search(r'ntSgenreCd[:：]\s*(\d+)', g)
    return (n(cls.group(1)) if cls else ''), (code.group(1) if code else ''), n(g)


cmap = collections.defaultdict(collections.Counter)
for r in rows:
    c, code, _ = parts(r.get('pia_genre'))
    if c and code:
        cmap[code][c] += 1
code2 = {k: v.most_common(1)[0][0] for k, v in cmap.items()}

ok, bad, unk = [], [], []
for r in sorted(rows, key=lambda x: x['id']):
    e = by.get(r['id'])
    if not e or e.get('genre') != 'new':
        continue
    leaf = n((e.get('_piaSub') or '').split('/')[-1])
    c, code, whole = parts(r.get('pia_genre'))
    # ページのジャンル番号を最優先（エージェントの「分類」はぴあの細かい札＝東京六大学野球連盟・大相撲 など）
    got = n(PIA_GENRE_CD.get(code, '')) or c or code2.get(code, '')
    if not leaf:
        unk.append((e, '登録に _piaSub が無い', r.get('pia_genre')))
    elif got:
        (ok if got == leaf else bad).append((e, got, r.get('pia_genre')))
    elif leaf in whole:
        ok.append((e, leaf, r.get('pia_genre')))
    else:
        unk.append((e, '分類名が取れない', r.get('pia_genre')))
print('一致 %d / 食い違い %d / 判定できない %d（読み直し %d件のうち新着にいるもの）' % (len(ok), len(bad), len(unk), len(ok) + len(bad) + len(unk)))
for e, got, g in bad:
    print('  ✗ id%d %s ／ 登録「%s」 実「%s」 ｜ %s' % (e['id'], e['name'][:30], e.get('_piaSub'), got, g))
for e, why, g in unk:
    print('  ？ id%d %s ／ 登録「%s」 %s ｜ %s' % (e['id'], e['name'][:30], e.get('_piaSub'), why, g))
