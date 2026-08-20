# -*- coding: utf-8 -*-
"""cand_countdown_0710.json を build_pia_entries で機械構築 → genre:new で投入 → NEW_ORDER 追記。
既存の新着プール(46件)は消さず、末尾に足す（投入順固定 [[feedback_new_list_order_lock]]）。"""
import re, io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/cand_countdown_0710.json'],
                   capture_output=True, timeout=1800)
try:
    built = json.loads(r.stdout.decode('utf-8', 'replace'))
except Exception as e:
    sys.stderr.buffer.write(r.stdout[:2000]); sys.stderr.buffer.write(r.stderr[-2000:])
    print('BUILD PARSE FAIL', e); sys.exit(1)
json.dump(built, open('tmp/built_countdown_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

cand_ids = [c['newid'] for c in json.load(open('tmp/cand_countdown_0710.json', encoding='utf-8'))]
dropped = [i for i in cand_ids if i not in [b['id'] for b in built]]

for b in built:
    b['genre'] = 'new'
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
existing = {e['id'] for e in EVENTS}
add = [b for b in built if b['id'] not in existing]
EVENTS.extend(add)
out = idx[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + idx[m.end():]

mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
cur = [x.strip() for x in mo.group(1).split(',') if x.strip()] if mo else []
cur += [str(b['id']) for b in sorted(add, key=lambda x: x['id'])]
out = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[' + ', '.join(cur) + r']\2', out, count=1)

open('index.html.bak_0710_countdown', 'w', encoding='utf-8').write(idx)
open('index.html', 'w', encoding='utf-8').write(out)

print('=== build %d / cand %d ===' % (len(built), len(cand_ids)))
if dropped: print('DROPPED(build落ち):', dropped)
print('投入 %d件 / NEW_ORDER %d件' % (len(add), len(cur)))
from collections import Counter
print('下書き_genre:', dict(Counter(b.get('_genre', '?') for b in add)))
