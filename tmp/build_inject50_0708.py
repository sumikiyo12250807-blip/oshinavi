# -*- coding: utf-8 -*-
"""cand50をbuild_pia_entriesで機械構築→genre:newでindex.htmlに投入→NEW_ORDER更新。
複合bash禁止のため build もsubprocessで内包し1発実行。"""
import re, io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1) build
r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/cand50_0708.json'],
                   capture_output=True, timeout=900)
try:
    built = json.loads(r.stdout.decode('utf-8', 'replace'))
except Exception as e:
    sys.stderr.buffer.write(r.stdout[:2000]); sys.stderr.buffer.write(r.stderr[-2000:])
    print('BUILD PARSE FAIL', e); sys.exit(1)
json.dump(built, open('tmp/built50_0708.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

cand_ids = [c['newid'] for c in json.load(open('tmp/cand50_0708.json', encoding='utf-8'))]
built_ids = [b['id'] for b in built]
dropped = [i for i in cand_ids if i not in built_ids]

# 2) genre:new 強制、投入
for b in built:
    b['genre'] = 'new'
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
existing = {e['id'] for e in EVENTS}
add = [b for b in built if b['id'] not in existing]
EVENTS.extend(add)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
out = idx[:m.start()] + m.group(1) + new_arr + m.group(3) + idx[m.end():]

# 3) NEW_ORDER 更新
add_ids = sorted(b['id'] for b in add)
no = '[' + ', '.join(str(i) for i in add_ids) + ']'
out, n = re.subn(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>' + no + r'\2', out, count=1)

open('index.html.bak_0708_newpool', 'w', encoding='utf-8').write(idx)
open('index.html', 'w', encoding='utf-8').write(out)

print('=== build %d / cand %d ===' % (len(built), len(cand_ids)))
if dropped:
    print('DROPPED(build落ち):', dropped)
print('投入 %d件 id%d..%d / NEW_ORDER %d件 / NEW_ORDER置換=%d' %
      (len(add), add_ids[0], add_ids[-1], len(add_ids), n))
from collections import Counter
c = Counter(b.get('_genre', '?') for b in add)
print('下書き_genre:', dict(c))
