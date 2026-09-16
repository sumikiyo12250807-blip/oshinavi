# -*- coding: utf-8 -*-
"""X準備の総ざらい（完全版）後半の候補を index.html と機械で突き合わせる（2026-09-16 夜）。
判定は「同じ呼び名のエントリに、その公演日を含む枠があるか」＝あれば取りこぼしではない。
使い方: python tmp/x0917/gapcheck2.py
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

Q = [
    ('沢田研二', '10/8'),
    ('沢田研二', '11/16'),
    ('沢田研二', '11/2'),
    ('神はサイコロを振らない', '11/29'),
    ('イルカ', '10/27'),
    ('イルカ', '9/18'),
    ('キングズ・シンガーズ', '12/8'),
    ('中川晃教', '12/2'),
    ('佐野元春', '9/26'),
    ('原田真二', '11/7'),
    ('名古屋港水族館', '4/1'),
    ('春風亭一之輔', '11/7'),
    ('柳家花緑', '10/24'),
    ('森山直太朗', 'R9年 1/7'),
    ('綾小路きみまろ', '12/1'),
    ('綾小路きみまろ', '12/3'),
]


def norm(x):
    return re.sub(r'[\s　・]', '', unicodedata.normalize('NFKC', x or '')).lower()


src = io.open('index.html', encoding='utf-8').read()
events = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

for name, md in Q:
    n = norm(name)
    ents = [e for e in events if n in norm((e.get('artist') or '') + (e.get('name') or ''))]
    hit = [(e['id'], t['type']) for e in ents
           for t in (e.get('tickets') or []) if md in (t.get('type') or '')]
    if hit:
        msg = '枠あり id%d %s' % (hit[0][0], hit[0][1][:40])
    elif ents:
        msg = '⚠ 登録%d件（%s）だが %s の枠なし' % (
            len(ents), ','.join(str(e['id']) for e in ents[:4]), md)
    else:
        msg = '⚠ 登録なし'
    print('%-22s %-9s → %s' % (name, md, msg))
