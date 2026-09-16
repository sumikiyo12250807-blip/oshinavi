# -*- coding: utf-8 -*-
"""新着プール（genre:new）のうち、ぴあ由来のものを全部拾う（読むだけ・2026-09-16 朝）。
9/15 に入れた分（9910〜10760）は初めての読み直し、9/14 の残り（読み直し1回済み）は2回目。
出力: tmp/recheck_todo_0916.txt ＝「id<TAB>ぴあURL…」の行（登録値は出さない＝独立再導出用）
使い方: python tmp/recheck_pick_0916.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in us:
            us.append(u)
    return us


todo, nopia = [], []
for e in sorted(ev, key=lambda x: x['id']):
    if e.get('genre') != 'new':
        continue
    us = pia_urls(e)
    if not us:
        nopia.append(e['id'])
        continue
    todo.append((e['id'], us))
with io.open('tmp/recheck_todo_0916.txt', 'w', encoding='utf-8') as f:
    for i, us in todo:
        f.write('%s\t%s\n' % (i, ' '.join(us)))
lo = [i for i, _ in todo if i < 9910]
hi = [i for i, _ in todo if i >= 9910]
print('新着プールのぴあ由来 %d件（9/14以前 %d件・9/15以降 %d件）→ tmp/recheck_todo_0916.txt' % (len(todo), len(lo), len(hi)))
print('ぴあURL無し %d件: %s' % (len(nopia), nopia))
