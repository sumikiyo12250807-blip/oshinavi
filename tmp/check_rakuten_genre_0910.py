# -*- coding: utf-8 -*-
"""ぴあ以外の新着について、売り場URLのジャンル階層と _genre を突き合わせる。読み取り専用。"""
import json, sys, io, os, re, urllib.parse
sys.stdout = io.TextIOWrapper(open(sys.__stdout__.fileno(), 'wb', closefd=False), encoding='utf-8')

IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
src = open(IDX, encoding='utf-8').read()
i = src.index('const EVENTS = [')
start = src.index('[', i)
depth, j, instr, esc = 0, start, False, False
while j < len(src):
    c = src[j]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    j += 1
events = json.loads(src[start:j+1])
new = [e for e in events if e.get('genre') == 'new']
nonpia = [e for e in new if not (e.get('links') or {}).get('pia')]

for e in nonpia:
    L = e.get('links') or {}
    u = L.get('rakuten') or L.get('eplus') or L.get('lawson') or ''
    real = u
    m = re.search(r'murl=([^&]+)', u)
    if m:
        real = urllib.parse.unquote(m.group(1))
    path = urllib.parse.urlparse(real).path
    print('id%s\t_genre=%s\t_srcgenre=%s\t%s\t%s' % (
        e.get('id'), e.get('_genre') or '(空)', e.get('_srcgenre') or '(無)',
        (e.get('artist') or '')[:40], path))
