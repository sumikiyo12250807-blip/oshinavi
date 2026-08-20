# -*- coding: utf-8 -*-
"""削除ゲート提示用のマークダウン（短ラベル形式）を index.html の登録値から生成する。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
byid = {e['id']: e for e in EVENTS}

A = [902, 1031, 1183, 1773, 2526, 2691]
B = [557, 914, 977, 980, 1256, 1342, 1586, 1775, 1807, 2139, 2374, 2753, 3150, 3452,
     3476, 3505, 3693, 3725, 4078, 4091, 4096, 4097, 4129, 4141]
E = [3022]


def line(i):
    e = byid[i]
    links = e.get('links') or {}
    u = links.get('pia') or ''
    if not u:
        for t in (e.get('tickets') or []):
            if t.get('url'):
                u = t['url']; break
    nm = e.get('name') or e.get('artist') or ''
    nm = re.sub(r'\s+', ' ', nm)[:38]
    return '%d %s（%s %s）[確認](%s)' % (i, nm, e.get('prefecture', ''), e.get('date', ''), u)


for t, ids in (('A', A), ('B', B), ('E', E)):
    print('### %s' % t)
    for i in ids:
        print('- ' + line(i))
