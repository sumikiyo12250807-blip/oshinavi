# -*- coding: utf-8 -*-
import collections, datetime, io, json, os, re, sys
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
_o = sys.stdout
import build_artist_pages as B
sys.stdout = _o
sys.stdout.reconfigure(encoding='utf-8')
today = datetime.date.today()
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
w = collections.Counter()
for e in ev:
    if e.get('genre') != 'new' and e.get('verified') is True and B.ticket_rows(e, today) and not B.artist_names(e):
        for n in B.work_names(e):
            w[n] += 1
print('作品ページ', len(w), '件数', sum(w.values()))
for n in ['ミュージカル『ファインディング・ネバーランド』', 'ミュージカル『RENT』', '『第九』', '『くるみ割り人形』']:
    print(n, w.get(n))
import random
random.seed(1)
print(random.sample(sorted(w), 40))
