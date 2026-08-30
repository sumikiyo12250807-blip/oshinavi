# -*- coding: utf-8 -*-
import urllib.request, re, io, sys, os, time, json, html as _html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
OUT='tmp/_agentP1_html'
os.makedirs(OUT, exist_ok=True)
rows=[l.rstrip('\n') for l in open('tmp/_poolgrp1_0831.txt',encoding='utf-8') if l.strip()]
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=40) as r:
        final=r.geturl(); body=r.read().decode('utf-8','replace')
    if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
        raise RuntimeError('SORRY')
    return body
start=int(sys.argv[1]); end=int(sys.argv[2])
for line in rows[start:end]:
    p=line.split('|')
    eid=p[0]; url=p[5]
    fp=os.path.join(OUT,eid+'.html')
    if os.path.exists(fp) and os.path.getsize(fp)>20000:
        print(eid,'cached'); continue
    ok=False
    for attempt in range(4):
        try:
            b=fetch(url)
            if 'ticketSalesCard-2024__status' not in b and attempt<3:
                time.sleep(6); continue
            open(fp,'w',encoding='utf-8').write(b)
            print(eid,'ok',len(b), b.count('ticketSalesCard-2024__status'))
            ok=True; break
        except Exception as e:
            print(eid,'retry',type(e).__name__,str(e)[:60]); time.sleep(8)
    if not ok:
        print(eid,'FAIL')
    time.sleep(2.5)
