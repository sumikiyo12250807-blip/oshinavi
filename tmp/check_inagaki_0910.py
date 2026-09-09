# -*- coding: utf-8 -*-
"""投稿文とindex.htmlで「JUNICHI INAGAKI」まわりの文字を1つずつ確かめる（改行や妙な空白が無いか）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

t = io.open('tmp/x_posts_0910.md', encoding='utf-8', newline='').read()
for m in re.finditer(r'JUNICHI.{0,30}', t, re.S):
    s = m.group(0)
    print('本文:', repr(s))
    print('  1文字ずつ:', ' '.join('%s(U+%04X)' % (c if c not in '\r\n' else '\\n', ord(c)) for c in s[:20]))
    print()

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))
for e in EV:
    if 'INAGAKI' in (e.get('name') or ''):
        n = e['name']
        print('index.htmlの登録名:', repr(n))
        print('  1文字ずつ:', ' '.join('%s(U+%04X)' % (c, ord(c)) for c in n[:20]))
