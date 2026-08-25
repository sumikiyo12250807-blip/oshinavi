# -*- coding: utf-8 -*-
import json, glob, io, sys, collections, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
c = collections.Counter()
for f in sorted(glob.glob(r'C:/Users/user/oshinavi/tmp/v1_0825/v_*.json')):
    rows = json.load(open(f, encoding='utf-8'))
    for r in rows:
        if r['state'] not in ('受付中','発売前'):
            c[(os.path.basename(f), r['statustext'])] += 1
for k,v in sorted(c.items()):
    print(k[0], '|', k[1], '|', v)
