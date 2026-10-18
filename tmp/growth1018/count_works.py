# -*- coding: utf-8 -*-
import collections, datetime, io, json, os, re, sys, unicodedata
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
_o = sys.stdout
import build_artist_pages as B
sys.stdout = _o
sys.stdout.reconfigure(encoding='utf-8')
today = datetime.date.today()
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
miss = [e for e in ev if e.get('genre') != 'new' and e.get('verified') is True and B.ticket_rows(e, today) and not B.artist_names(e)]
BR = re.compile(r'[『「]([^』」]{2,40})[』」]')
hit = collections.Counter()
ex = collections.defaultdict(list)
for e in miss:
    src = unicodedata.normalize('NFKC', (e.get('artist') or '') + ' ' + (e.get('name') or ''))
    m = BR.search(src)
    if m:
        t = m.group(1).strip()
        hit[t] += 1
        ex[t].append(e['id'])
print('漏れ', len(miss), '／作品名が読める', sum(hit.values()), '件・作品', len(hit))
for t, n in hit.most_common(40):
    print(' ', n, t)
