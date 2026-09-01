# -*- coding: utf-8 -*-
import json, re, io

NEW_IDS = [6274,6287,6288,6290,6295,6303,6304,6306,6317,6330,6332,6342,6343,6344,6345,6351,6352]
OLD_IDS = [2338,4491,4509,5291,695,4178,4502,6080,413,4670,3551,4245,41,450,2362,4223,4843,2111,1960,1961,4732,3557,4207,3638,3406]

with io.open('tmp/_newbuilt_0902.json', encoding='utf-8') as f:
    new = json.load(f)
with io.open('index.html', encoding='utf-8') as f:
    h = f.read()
old = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
nmap = {e.get('id'): e for e in new}
omap = {e.get('id'): e for e in old}

o = io.open('tmp/dupinv2_0902.txt', 'w', encoding='utf-8')
def p(s): o.write(s + u'\n')

def dump(tag, e):
    if e is None:
        p(u'%s MISSING' % tag); return
    p(u'%s id=%s %s | %s | %s' % (tag, e.get('id'), e.get('name',''), e.get('date',''), e.get('venue','')))
    p(u'   links: %s' % json.dumps(e.get('links'), ensure_ascii=False))
    p(u'   _piaSub: %s' % json.dumps(e.get('_piaSub'), ensure_ascii=False))
    for i,t in enumerate(e.get('tickets') or []):
        if t.get('url'): p(u'   Turl%d %s | %s' % (i, t.get('type',''), t['url']))

for i in NEW_IDS: dump(u'NEW', nmap.get(i))
p(u'')
for i in OLD_IDS: dump(u'OLD', omap.get(i))
o.close()
print('ok')
