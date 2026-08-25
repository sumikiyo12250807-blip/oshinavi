# -*- coding: utf-8 -*-
import json, subprocess, sys, time, os

ROOT = r'C:/Users/user/oshinavi'
IN = os.path.join(ROOT, 'tmp/verify_in_1_0825.json')
OUTDIR = os.path.join(ROOT, 'tmp/v1_0825')
items = json.load(open(IN, encoding='utf-8'))
print('items:', len(items))

for i, it in enumerate(items):
    eid = str(it['id'])
    dst = os.path.join(OUTDIR, 'v_%s.json' % eid)
    errdst = os.path.join(OUTDIR, 'e_%s.txt' % eid)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        continue
    ok = False
    for attempt in range(4):
        with open(dst, 'wb') as fo, open(errdst, 'wb') as fe:
            rc = subprocess.call([sys.executable, os.path.join(ROOT, 'tools/pia_tickets.py'),
                                  it['pia'], '--all', '--json'], stdout=fo, stderr=fe)
        if rc == 0 and os.path.getsize(dst) > 0:
            ok = True
            break
        time.sleep(6 + attempt * 6)
    print(i, eid, 'OK' if ok else 'FAIL')
    sys.stdout.flush()
    time.sleep(2.0)
print('done')
