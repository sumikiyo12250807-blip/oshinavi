# -*- coding: utf-8 -*-
"""新着プールのジャンル下書き(_genre)の誤りを直す（genreは"new"のまま＝振り分けではない）。

ぴあのbundleページはカテゴリを返さないことがあり(_piaSub空)、名前ベースfallbackで
engekiに倒れる。ジャンルはイベント形式でなく**アーティスト**で決まる
（[[project_vendor_genre_autoassign]]）。
 3696 Stray Kids  engeki → kpop （4大ドームのK-POPツアー）
 3699 NOISEMAKER  engeki → rock （ライブハウス16本のロックバンドツアー）
🚨CRLF維持（[[feedback_index_html_crlf_preserve]]）。
"""
import io
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'index.html')
FIX = {3696: ('engeki', 'kpop'), 3699: ('engeki', 'rock')}

h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

for i, (was, to) in FIX.items():
    e = byid[i]
    assert e.get('genre') == 'new', 'id%d が genre:new でない' % i
    assert e.get('_genre') == was, 'id%d の下書きが %s でなく %s' % (i, was, e.get('_genre'))
    e['_genre'] = to

shutil.copyfile(P, os.path.join(ROOT, 'index.html.bak_0804_draft_fix'))
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(P, 'w', encoding='utf-8', newline='').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
raw = open(P, 'rb').read()
after = {e['id']: e.get('_genre') for e in json.loads(
    re.search(r'(  const EVENTS = )(\[.*?\])(;)', io.open(P, encoding='utf-8', newline='').read(), re.S).group(2))
    if e['id'] in FIX}
print('fixed=%s  newpool=%d  stray_lf=%d'
      % (after, sum(1 for e in EVENTS if e.get('genre') == 'new'),
         raw.count(b'\n') - raw.count(b'\r\n')))
