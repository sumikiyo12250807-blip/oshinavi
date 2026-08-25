# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))
for it in items:
    eid=str(it['id']); u=it['pia']
    if 'Bundle' not in u: continue
    h=open(os.path.join(BASE,'tmp','w_html','%s.html'%eid), encoding='utf-8').read()
    evs=set(re.findall(r'ticketInformation\.do\?[^"\']*eventCd=(\d+)', h))
    lots=set(re.findall(r'lotRlsCd=(\d+)', h))
    # links to other event.do pages (bundle child listing)
    childs=set(re.findall(r'event\.do\?eventCd=(\d+)', h))
    print('%s bundle=%s childEventCd=%d lotRls=%d ticketInfoEventCd=%s' % (eid, u.split('=')[-1], len(childs), len(lots), sorted(evs)))
