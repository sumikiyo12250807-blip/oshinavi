# -*- coding: utf-8 -*-
"""artist ページから漏れている「買える枠のあるエントリ」を数える（読むだけ）。"""
import collections, datetime, io, json, os, re, sys
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
_o = sys.stdout
import build_artist_pages as B
sys.stdout = _o
today = datetime.date.today()
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
live = [e for e in ev if e.get('genre') != 'new' and B.ticket_rows(e, today)]
miss = [e for e in live if not B.artist_names(e)]
print('買える枠のあるエントリ', len(live), '／artist ページに載らない', len(miss))
g = collections.Counter(e.get('genre') for e in miss)
print('ジャンル別', g.most_common(15))
for e in miss:
    if e.get('genre') in ('musical', 'engeki', 'classic', 'fes', 'anime'):
        pass
ex = [e for e in miss if e.get('genre') == 'musical'][:15]
for e in ex:
    print('  ', e['id'], e.get('artist'))
