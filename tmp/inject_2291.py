# -*- coding: utf-8 -*-
"""build落ちのid2291をフェッチ再取得で救済投入。genre:new・NEW_ORDER末尾追加。"""
import re, io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/cand_2291.json'],
                   capture_output=True, timeout=300)
txt = r.stdout.decode('utf-8', 'replace')
built = json.loads(txt[txt.index('['):])
b = built[0]
b['genre'] = 'new'
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
if any(e['id'] == b['id'] for e in EVENTS):
    print('already present', b['id']); sys.exit(0)
EVENTS.append(b)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
out = idx[:m.start()] + m.group(1) + new_arr + m.group(3) + idx[m.end():]
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', out)
order = json.loads(mo.group(2))
if b['id'] not in order:
    order.append(b['id'])
out = out[:mo.start()] + mo.group(1) + json.dumps(order) + mo.group(3) + out[mo.end():]
open('index.html.bak_0709_inject2291', 'w', encoding='utf-8').write(idx)
open('index.html', 'w', encoding='utf-8').write(out)
print('投入 id%d / NEW_ORDER=%d / total=%d' % (b['id'], len(order), len(EVENTS)))
