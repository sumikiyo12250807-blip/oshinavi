# -*- coding: utf-8 -*-
"""build_pia_entries.py の出力(機械パース済エントリ・genre:new・T-SQUARE)を
index.html の EVENTS 末尾に追記し、NEW_ORDER をその投入idで更新する。
EVENTS は json.dumps(indent=2) 形式・キー順保持で書き戻す。
下書きフィールド(_genre/_extraGenres/_piaSub)はレビュー振り分け用に残す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

built = json.load(open('tmp/built_0629_final.json', encoding='utf-8'))

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
exist_ids = {e['id'] for e in EVENTS}

# 既存eventCdを集めて重複ガード(全角/半角の取りこぼし対策・eventCd一致は確実な重複)
def ecds(ev):
    s = set()
    for u in [(ev.get('links') or {}).get('pia')] + [t.get('url') for t in ev.get('tickets', [])]:
        if u:
            for mm in re.finditer(r'event(?:Bundle)?Cd=(\w+)', u):
                s.add(mm.group(1))
    return s
exist_ecd = set()
for e in EVENTS:
    exist_ecd |= ecds(e)

add, skip = [], []
for e in built:
    if e['id'] in exist_ids:
        skip.append((e['id'], 'id重複')); continue
    dup = ecds(e) & exist_ecd
    if dup:
        skip.append((e['id'], 'eventCd重複%s' % dup)); continue
    add.append(e)

EVENTS.extend(add)
new_ids = [e['id'] for e in add]

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
no_new = '[' + ', '.join(str(i) for i in sorted(new_ids)) + ']'
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
h2, n = re.subn(r'(NEW_ORDER\s*=\s*\[)[0-9,\s]*(\])', 'NEW_ORDER = ' + no_new, h2)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html.bak_0629_newpool', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print('投入 %d件 ids %s' % (len(add), '%d..%d' % (new_ids[0], new_ids[-1]) if new_ids else '-'))
print('skip:', skip)
print('NEW_ORDER 更新済 / backup: index.html.bak_0629_newpool')
