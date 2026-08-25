# -*- coding: utf-8 -*-
import json, os, time, urllib.request
BASE = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))
os.makedirs(os.path.join(BASE,'tmp','w_html'), exist_ok=True)
for it in items:
    eid = str(it['id']); p = os.path.join(BASE,'tmp','w_html','%s.html'%eid)
    if os.path.exists(p) and os.path.getsize(p) > 5000: continue
    try:
        req = urllib.request.Request(it['pia'], headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl(); body = r.read().decode('utf-8','replace')
        open(p,'w',encoding='utf-8').write(body)
        print(eid, len(body), 'SORRY' if 'sorry.pia' in final else '')
    except Exception as e:
        print(eid, 'ERR', e)
    time.sleep(2.5)
