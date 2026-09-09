# -*- coding: utf-8 -*-
"""新着(genre=="new")の全件を id/名前/会場/_piaSub/_genre/リンクで一覧にする。読み取り専用。"""
import json, sys, io, os
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

for e in new:
    L = e.get('links') or {}
    src_kind = 'pia' if L.get('pia') else (','.join(k for k, v in L.items() if v) or '-')
    print('%s\t%s\t%s\t%s\t%s\t%s' % (
        e.get('id'), e.get('_genre') or '(空)', e.get('_piaSub') or '(空)',
        (e.get('artist') or e.get('name') or '')[:60],
        (e.get('venue') or e.get('place') or '')[:40], src_kind))
