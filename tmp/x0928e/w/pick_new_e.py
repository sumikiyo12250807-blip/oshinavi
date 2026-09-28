# -*- coding: utf-8 -*-
"""built_new.json から既存へ足し込む分（NAME_MERGE）を外し、新規投入用 inject.json を作る（tmp/x0928/pick_new.py の夜版）。
25276 Chevon 大阪（2027ツアー）は 25275 Chevon（同じ2027ツアーのオフィシャル先行）に枠を足して1エントリにする。
id は index.html の今の最大id+1 から振る。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
NAME_MERGE = {25251, 25252, 25253, 25284, 25270, 25255}
INTO_NEW = {25276: 25275}
src = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
mx = max(e['id'] for e in ev)
cds = set()
for e in ev:
    for u in [json.dumps(e.get('links') or {}, ensure_ascii=False)] + [t.get('url') or '' for t in e.get('tickets') or []]:
        cds.update(re.findall(r'event(?:Bundle)?Cd=(\w+)', u))
built = json.load(open('tmp/x0928e/w/built_new.json', encoding='utf-8'))
by = {b['id']: b for b in built}
for s, d in INTO_NEW.items():
    dst = by[d]
    for t in by[s]['tickets']:
        t = dict(t)
        if not t.get('url'):
            t['url'] = by[s]['links']['pia']
        dst['tickets'].append(t)
    if by[s]['date'] > dst['date']:
        dst['date'] = by[s]['date']
    print('畳んだ %d → %d（枠 %d）' % (s, d, len(by[s]['tickets'])))
out = []
nid = mx + 1
for b in built:
    if b['id'] in NAME_MERGE or b['id'] in INTO_NEW:
        continue
    c = re.search(r'event(?:Bundle)?Cd=(\w+)', (b.get('links') or {}).get('pia') or '').group(1)
    if c in cds:
        print('!! 既に登録にある eventCd=%s（%s）＝外す' % (c, b.get('artist')))
        continue
    print('  %d → id%d %s' % (b['id'], nid, b.get('artist')))
    b = dict(b, id=nid)
    out.append(b)
    nid += 1
json.dump(out, io.open('tmp/x0928e/w/inject.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('最大id %d → 新規 %d件 id%d〜%d / 枠 %d' % (mx, len(out), out[0]['id'], out[-1]['id'], sum(len(e['tickets']) for e in out)))
