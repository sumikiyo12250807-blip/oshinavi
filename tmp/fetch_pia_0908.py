# -*- coding: utf-8 -*-
"""検証対象12件のぴあ実ページを取得し、生HTMLと券種カードのJSONを保存する。
ぴあの負荷を避けるため1件ごとに3秒あける。sorry/429 は「照合できなかった」として記録。"""
import json, os, sys, time, io, re, urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.makedirs('tmp/pia0908', exist_ok=True)

sel = json.load(open('tmp/audit_new_0908.json', encoding='utf-8'))

results = {}
for e in sel:
    eid = e['id']
    url = e['links']['pia']
    path = 'tmp/pia0908/%s.html' % eid
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        print(eid, 'キャッシュ済み')
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl()
            body = r.read().decode('utf-8', 'replace')
        if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
            print(eid, 'SORRY 混雑ページ')
            open('tmp/pia0908/%s.ERR' % eid, 'w').write('sorry')
        else:
            open(path, 'w', encoding='utf-8').write(body)
            print(eid, 'OK', len(body))
    except Exception as ex:
        print(eid, 'ERR', type(ex).__name__, str(ex)[:120])
        open('tmp/pia0908/%s.ERR' % eid, 'w').write(str(ex)[:200])
    time.sleep(3)
print('done')
