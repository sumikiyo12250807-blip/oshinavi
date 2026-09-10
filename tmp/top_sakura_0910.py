# -*- coding: utf-8 -*-
"""新着のいちばん上を櫻坂46（id7822）にする。

ユーザー指示（2026-09-10）＝「しんちゃくのうえのほうにのせておいて」。
今日足した9件は全部上位に来ているが、**いちばんの目玉を先頭に**置く。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TOP = 7822

src = io.open('index.html', encoding='utf-8').read()
mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', src, re.S)
arr = json.loads(mo.group(2))
if arr[0] == TOP:
    print('もう先頭にある')
    sys.exit(0)
arr2 = [TOP] + [i for i in arr if i != TOP]
print('NEW_ORDER 先頭 %s → %s' % (arr[:4], arr2[:4]))
out = src[:mo.start()] + mo.group(1) + json.dumps(arr2) + mo.group(3) + src[mo.end():]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)

h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
pool = {e['id'] for e in ev if e.get('genre') == 'new'}
no = json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h, re.S).group(1))
print('新着プール %d / NEW_ORDER %d / 差 %s %s'
      % (len(pool), len(no), sorted(pool - set(no))[:3], sorted(set(no) - pool)[:3]))
print('書き込み完了')
