# -*- coding: utf-8 -*-
import urllib.request, sys, io, os, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\Users\user\oshinavi'
D = os.path.join(ROOT,'tmp','verify_B_html')
os.makedirs(D, exist_ok=True)
lines = [l.rstrip('\n') for l in open(os.path.join(ROOT,'tmp','verify_list_B_0902.txt'), encoding='utf-8') if l.strip()]
for ln in lines:
    p = ln.split('\t')
    if len(p) < 2: continue
    eid, url = p[0].strip(), p[1].strip()
    dest = os.path.join(D, eid + '.html')
    if os.path.exists(dest) and os.path.getsize(dest) > 5000:
        print(eid, 'cached'); continue
    ok = False
    for attempt in (1,2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                final = r.geturl(); body = r.read().decode('utf-8','replace')
            if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
                raise RuntimeError('sorry page')
            open(dest,'w',encoding='utf-8').write(body)
            ok = True; break
        except Exception as e:
            err = str(e)
            if attempt == 1: time.sleep(20)
    print(eid, 'OK' if ok else 'FAIL', flush=True)
    time.sleep(2)
print('DONE')
