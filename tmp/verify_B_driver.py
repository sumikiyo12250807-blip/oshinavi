# -*- coding: utf-8 -*-
import subprocess, sys, io, json, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\Users\user\oshinavi'
lines = [l.rstrip('\n') for l in open(os.path.join(ROOT,'tmp','verify_list_B_0902.txt'), encoding='utf-8') if l.strip()]
out = {}
for ln in lines:
    parts = ln.split('\t')
    if len(parts) < 2:
        continue
    eid, url = parts[0].strip(), parts[1].strip()
    rec = {'id': eid, 'url': url}
    for attempt in (1, 2):
        p = subprocess.run([sys.executable, os.path.join(ROOT,'tools','pia_tickets.py'), url, '--all', '--json'],
                           capture_output=True, cwd=ROOT)
        so = p.stdout.decode('utf-8','replace')
        se = p.stderr.decode('utf-8','replace')
        if p.returncode == 0 and so.strip().startswith('['):
            try:
                rec['rows'] = json.loads(so)
                rec['ok'] = True
                break
            except Exception as e:
                rec['err'] = 'JSON parse: %s' % e
        else:
            rec['err'] = (se.strip()[-400:] or 'rc=%d' % p.returncode)
        if attempt == 1:
            time.sleep(20)
    if 'rows' not in rec:
        rec['ok'] = False
    n = len(rec.get('rows', []))
    b = len([r for r in rec.get('rows', []) if r['state'] in ('受付中','発売前')])
    print('%s  ok=%s  all=%d buyable=%d' % (eid, rec.get('ok'), n, b), flush=True)
    out[eid] = rec
    time.sleep(2)
json.dump(out, open(os.path.join(ROOT,'tmp','verify_B_0902_raw.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE')
