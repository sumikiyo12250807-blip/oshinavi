# -*- coding: utf-8 -*-
"""新着プール（genre:new＝振り分け前）にある、明日9/15〜9/17に発売が始まる枠を並べる（読むだけ・9/14夜の便）。
X素材（tmp/x0914/material.md）は ?genre= の着地先に出ない新着プールを入れていない＝ここで中身を見て、
振り分けてから素材に入れるか、今夜は出さないかを決める。
使い方: python tmp/x0914/newpool_0915.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DAYS = ('2026-09-15', '2026-09-16', '2026-09-17')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
for e in ev:
    if e.get('genre') != 'new':
        continue
    ts = [t for t in e.get('tickets') or [] if t.get('startDate') in DAYS and not t.get('soldout')]
    if ts:
        print('id%-5s [%s] %s ｜%s' % (e['id'], e.get('_genre') or '?', (e.get('name') or '')[:40], e.get('_piaSub') or ''))
        for t in ts:
            print('       %s ｜%s' % (t.get('type'), t.get('url') or (e.get('links') or {}).get('pia') or ''))
