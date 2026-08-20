# -*- coding: utf-8 -*-
"""ヒール再構築(tmp/heal_ids.json)と現行index.htmlの枠数差分だけ出す。"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
evs = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}
d = json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))
n = 0
for it in d:
    cur = evs[it['id']]
    a = set(t['type'] for t in (cur.get('tickets') or []))
    b = set(t['type'] for t in (it.get('tickets') or []))
    if a != b:
        n += 1
        print('id=%d %s  現行%d枠 → ヒール%d枠' % (it['id'], cur.get('name'), len(a), len(b)))
        for t in sorted(b - a):
            print('   ＋ ' + t)
        for t in sorted(a - b):
            print('   － ' + t)
print('差分ありエントリ %d件 / 対象 %d件' % (n, len(d)))
