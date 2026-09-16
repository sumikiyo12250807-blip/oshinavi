# -*- coding: utf-8 -*-
"""新着プールのうち 9/14 に入れたぴあ由来（id 8385〜9903）で、まだ独立の読み直しをしていないものを選ぶ（読むだけ・2026-09-15 朝）。
読み直し済み＝前日セッションの scratchpad にある *_result.json に id が載っているもの。
出力: tmp/recheck_todo_0915.txt ＝「id<TAB>ぴあURL…」の行（登録値は出さない＝独立再導出用）
使い方: python tmp/recheck_pick_0915.py
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
OLD_SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
LO, HI = 8385, 9903
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

seen = set()
for p in glob.glob(os.path.join(OLD_SP, '*result*.json')):
    if 'debug' in p:
        continue
    try:
        rows = json.load(io.open(p, encoding='utf-8'))
    except Exception:
        continue
    if isinstance(rows, list):
        seen |= {r.get('id') for r in rows if isinstance(r, dict)}


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in us:
            us.append(u)
    return us


todo, done, nopia = [], [], []
for e in sorted(ev, key=lambda x: x['id']):
    if e.get('genre') != 'new' or not (LO <= e['id'] <= HI):
        continue
    us = pia_urls(e)
    if not us:
        nopia.append(e['id'])
        continue
    (done if e['id'] in seen else todo).append((e['id'], us))
with io.open('tmp/recheck_todo_0915.txt', 'w', encoding='utf-8') as f:
    for i, us in todo:
        f.write('%s\t%s\n' % (i, ' '.join(us)))
print('対象（9/14 のぴあ由来の新着）%d件 ／ 読み直し済み %d件 ／ 未読 %d件 → tmp/recheck_todo_0915.txt' % (len(todo) + len(done), len(done), len(todo)))
print('ぴあURL無し: %s' % nopia)
