# -*- coding: utf-8 -*-
"""投入済みのTIGETエントリの tickets を、直した規則で作り直した内容に**現物で置き換える**。
🚨エントリを作り直さない＝id は据え置き（[[feedback_new_list_order_lock]]）。
   置き換えるのは tickets だけ。飛び先(url)は同じページなので変わらない。
   これで「同じバッジが並ぶ」二重と、名前がぶつかって区別がつかない枠が直る。
"""
import re, json, io, glob

# 作り直した結果を TIGETのURL（events/<id>）で引ける形にする
newby = {}
for f in ('tmp/rebuild_yt_0918.json', 'tmp/rebuild_wide_0918.json'):
    for e in json.load(open(f, encoding='utf-8'))['entries']:
        ids = tuple(sorted({m for u in [e['links'].get('tiget')] + (e.get('_merged_from') or [])
                            for m in re.findall(r'/events/(\d+)', u or '')}))
        newby[ids] = e

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

o = io.open('tmp/retype_tiget_0918.txt', 'w', encoding='utf-8')
hit = miss = same = 0
for e in EVENTS:
    if not (11317 <= e['id'] <= 13230):
        continue
    ids = tuple(sorted({x for t in (e.get('tickets') or [])
                        for x in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or '')}))
    n = newby.get(ids)
    if not n:
        miss += 1
        o.write('❓ id%d 作り直しが見つからない %s %s\n' % (e['id'], ids, (e.get('name') or '')[:30]))
        continue
    before = [t.get('type') for t in e['tickets']]
    after = [t.get('type') for t in n['tickets']]
    if before == after:
        same += 1
        continue
    o.write('id%d %s ｜枠 %d→%d\n' % (e['id'], (e.get('name') or '')[:34], len(before), len(after)))
    for t in sorted(set(before) - set(after)):
        o.write('   − %s\n' % t[:70])
    for t in sorted(set(after) - set(before)):
        o.write('   ＋ %s\n' % t[:70])
    e['tickets'] = json.loads(json.dumps(n['tickets']))
    hit += 1

io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
o.write('\n差し替えた %d件 / そのままでよかった %d件 / 作り直しが無い %d件\n' % (hit, same, miss))
o.close()
