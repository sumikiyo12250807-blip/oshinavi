# -*- coding: utf-8 -*-
"""機械パース済みの音楽発売前61件(built_music_0708.json)をEVENTSに追記・NEW_ORDER更新。
eventCd重複を既存と突合してスキップ(harvestのin_db漏れ・朝の統合/削除後のズレ対策)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
built = json.load(open('tmp/built_music_0708.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

def eventcds(e):
    s = set()
    lp = (e.get('links') or {}).get('pia') or ''
    for u in [lp] + [t.get('url','') for t in e.get('tickets',[])]:
        for cd in re.findall(r'event(?:Bundle)?Cd=(\w+)', u or ''):
            s.add(cd)
    return s

existing_cds = set()
existing_ids = set()
for e in EVENTS:
    existing_ids |= {e.get('id')}
    existing_cds |= eventcds(e)

add, skip = [], []
for e in built:
    cds = eventcds(e)
    if e['id'] in existing_ids:
        skip.append((e['id'], e['name'][:26], 'id重複')); continue
    if cds & existing_cds:
        skip.append((e['id'], e['name'][:26], 'eventCd重複'+str(cds & existing_cds))); continue
    add.append(e)
    existing_cds |= cds

print(f"投入 {len(add)}件 / skip {len(skip)}件")
for s in skip:
    print("  skip", s)

if not DRY:
    EVENTS2 = EVENTS + add
    new_arr = json.dumps(EVENTS2, ensure_ascii=False, indent=2)
    h2 = h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():]
    mo = re.search(r'(NEW_ORDER\s*=\s*)(\[[^\]]*\])', h2)
    order = json.loads(mo.group(2))
    order = order + [e['id'] for e in add]
    h2 = h2[:mo.start()]+mo.group(1)+json.dumps(order)+h2[mo.end():]
    open('index.html.bak_0708_music_inject','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h2)
    print(f"written / NEW_ORDER={len(order)} / total={len(EVENTS2)}")
else:
    print("(DRY)")
