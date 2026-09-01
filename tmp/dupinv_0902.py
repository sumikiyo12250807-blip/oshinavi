# -*- coding: utf-8 -*-
import json, re, io, sys

NEW_IDS = [6274,6287,6288,6290,6295,6303,6304,6306,6317,6330,6332,6342,6343,6344,6345,6351,6352]
OLD_IDS = [2338,4491,4509,5291,695,4178,4502,6080,413,4670,3551,4245,41,450,2362,4223,4843,2111,1960,1961,4732,3557,4207,3638,3406]

with io.open('tmp/_newbuilt_0902.json', encoding='utf-8') as f:
    new = json.load(f)
with io.open('index.html', encoding='utf-8') as f:
    h = f.read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
old = json.loads(m.group(2))

nmap = {e.get('id'): e for e in new}
omap = {e.get('id'): e for e in old}

o = io.open('tmp/dupinv_0902.txt', 'w', encoding='utf-8')
def p(s):
    o.write(s + u'\n')

p(u'NEW keys sample: %s' % sorted(new[0].keys()))
p(u'NEW ticket keys sample: %s' % sorted((new[0].get('tickets') or [{}])[0].keys()))
p(u'')

def dump(tag, e):
    if e is None:
        p(u'%s  MISSING' % tag); return
    p(u'--- %s id=%s' % (tag, e.get('id')))
    p(u'  name  : %s' % e.get('name',''))
    p(u'  artist: %s' % e.get('artist',''))
    p(u'  date  : %s | venue: %s | area: %s | genre: %s' % (e.get('date',''), e.get('venue',''), e.get('area',''), e.get('genre','')))
    for k in ('desc','note','subtitle','eventCd','url','officialUrl','ticketUrl'):
        if e.get(k): p(u'  %-8s: %s' % (k, unicode(e[k])[:300] if sys.version_info[0]<3 else str(e[k])[:300]))
    for i, t in enumerate(e.get('tickets') or []):
        p(u'  T%d %s' % (i, json.dumps(t, ensure_ascii=False)))

for i in NEW_IDS:
    p(u'===== NEW %s =====' % i); dump(u'NEW', nmap.get(i))
p(u'')
for i in OLD_IDS:
    p(u'===== OLD %s =====' % i); dump(u'OLD', omap.get(i))
o.close()
print('ok')
