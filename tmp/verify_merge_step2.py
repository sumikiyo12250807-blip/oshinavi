# -*- coding: utf-8 -*-
"""同名グループの中身を突き合わせ、畳んではいけない兆候を機械で洗う"""
import re, json, unicodedata, sys, io, collections, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = r'C:\Users\user\oshinavi\index.html'
TODAY = '2026-09-04'
src = open(PATH, encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);', src, re.S).group(1))

def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[^0-9a-z\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]', '', s)
def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'): return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)

groups = collections.defaultdict(list)
for e in EVENTS: groups[norm(e.get('name',''))].append(e)
dg = {k:v for k,v in groups.items() if len(v)>=2 and k}

# キー抽出：ぴあ eventCd / rlsCd, 楽天, e+ の識別子
def ids_from_url(u):
    u = u or ''
    out = set()
    for m in re.finditer(r'eventCd=([0-9A-Za-z]+)', u): out.add('pia:'+m.group(1))
    for m in re.finditer(r'/event/(\d+)', u): out.add('rkt:'+m.group(1))
    for m in re.finditer(r'/sf/detail/(\d+)', u): out.add('eplus:'+m.group(1))
    return out

print('== グループごとの機械指標 ==')
print('name | ids | 会場重複 | 公演日重複 | 共有チケットURL識別子 | 券種語(車椅子/駐車/VIP/来場者側) | ジャンル')
rows=[]
SEAT_WORDS = ['車椅子','車いす','駐車','ビジター','ホーム','三塁','一塁','レフト','ライト','VIP','同伴','親子','託児','見切','立見','配信','グッズ','ペア']
for k,g in sorted(dg.items(), key=lambda kv:(-len(kv[1]),kv[0])):
    g = sorted(g, key=lambda x:x.get('id'))
    venues = [str(e.get('venue')) for e in g]
    dates  = [str(e.get('date')) for e in g]
    vdup = len(set(venues))<len(venues)
    ddup = len(set(dates))<len(dates)
    idsets = [set().union(*[ids_from_url(t.get('url')) for t in (e.get('tickets') or [])]) if e.get('tickets') else set() for e in g]
    shared = set()
    for i in range(len(idsets)):
        for j in range(i+1,len(idsets)):
            shared |= (idsets[i] & idsets[j])
    words = set()
    for e in g:
        for t in (e.get('tickets') or []):
            for w in SEAT_WORDS:
                if w in (t.get('type') or ''): words.add(w)
    rows.append((len(g), g[0].get('name'), [e.get('id') for e in g], vdup, ddup, len(shared), sorted(words),
                 sorted(set(str(e.get('genre')) for e in g))))
for r in sorted(rows, key=lambda x:(-x[0], x[1])):
    print('%d | %s | %s | venueDup=%s dateDup=%s | sharedUrlIds=%d | %s | %s' % (
        r[0], r[1], r[2], r[3], r[4], r[5], ','.join(r[6]), '/'.join(r[7])))
