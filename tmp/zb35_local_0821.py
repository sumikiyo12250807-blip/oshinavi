# -*- coding: utf-8 -*-
"""index.html の EVENTS から zb35 の35件を引き、tickets の中身（枠と販売期間）を吐く。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', 'rb').read().decode('utf-8')
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', h, re.S)
print('found=%s' % bool(m))
data = json.loads(m.group(1))
ids = [1554,1601,2748,3473,3509,3696,4035,4036,4050,4051,4057,4066,4080,4081,4083,4089,4094,4098,4100,4106,4114,4115,4117,4150,4156,4159,4163,4165,4167,4172,4175,4422,4423,4424,4425]
by = {e.get('id'): e for e in data}
for i in ids:
    e = by.get(i)
    if not e:
        print('id=%s NOT FOUND' % i); continue
    ts = e.get('tickets') or []
    print('--- id=%s %s | %s | date=%s | tickets=%d' % (i, e.get('title',''), e.get('venue',''), e.get('date',''), len(ts)))
    for t in ts:
        print('    [%s] %s | start=%s end=%s | soldout=%s saleEnded=%s | %s' % (
            t.get('type',''), t.get('dateLabel',''), t.get('startDate',''), t.get('date',''),
            t.get('soldout'), t.get('saleEnded'), (t.get('url') or '')[:80]))
