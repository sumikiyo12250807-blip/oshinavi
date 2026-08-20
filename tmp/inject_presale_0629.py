# -*- coding: utf-8 -*-
"""発売前バッチ(tmp/built_0629_presale.json)を既存EVENTSに追記。
eventCd重複は既存全エントリと照合して除外(既に入れた藍井エイル等も自動スキップ)。
NEW_ORDERは【全genre:new】から再計算(既存50件を消さない)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

built = json.load(open('tmp/built_0629_presale.json', encoding='utf-8'))

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
exist_ids = {e['id'] for e in EVENTS}

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
    if not e.get('tickets'):
        skip.append((e['id'], 'ticket空')); continue
    add.append(e)
    exist_ecd |= ecds(e)   # バッチ内重複も防ぐ

EVENTS.extend(add)
allnew = sorted(e['id'] for e in EVENTS if e.get('genre') == 'new')

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
no_new = '[' + ', '.join(str(i) for i in allnew) + ']'
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
h2, n = re.subn(r'(NEW_ORDER\s*=\s*\[)[0-9,\s]*(\])', 'NEW_ORDER = ' + no_new, h2)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html.bak_0629_presale', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h2)
print('発売前 追加 %d件: %s' % (len(add), [e['id'] for e in add]))
print('skip:', skip)
print('genre:new 合計 %d件' % len(allnew))
