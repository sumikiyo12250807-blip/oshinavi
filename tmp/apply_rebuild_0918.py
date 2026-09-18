# -*- coding: utf-8 -*-
"""エージェントの指摘を直した規則で組み直した結果を、投入済みに当てる。

やること（id は据え置き＝[[feedback_new_list_order_lock]]）
 ①登録エントリの tickets を、同じTIGETページから組み直したものに差し替える
 ②畳みすぎを解いた分（1エントリに畳んでいたのが別商品だった）は、**残りを新しいidで足す**
 ③組み直しに出てこなくなったもの（主催者の雛形）は消す
"""
import re, json, io

new_by_id = {}          # TIGETのイベントid → 組み直したエントリ
for f in ('tmp/rebuild_yt_0918.json', 'tmp/rebuild_wide_0918.json'):
    for e in json.load(open(f, encoding='utf-8'))['entries']:
        for x in re.findall(r'/events/(\d+)',
                            ' '.join([e['links'].get('tiget') or ''] + (e.get('_merged_from') or []))):
            new_by_id[x] = e

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])

o = io.open('tmp/apply_rebuild_0918.txt', 'w', encoding='utf-8')
swapped = unfolded = removed = same = 0
used = set()
drop_ids = []
add = []
for e in EVENTS:
    if not (11317 <= e['id'] <= 13230):
        continue
    tids = sorted({x for t in (e.get('tickets') or [])
                   for x in re.findall(r'tiget\.net/events/(\d+)', t.get('url') or '')})
    hits = []
    for x in tids:
        n = new_by_id.get(x)
        if n is not None and id(n) not in {id(y) for y in hits}:
            hits.append(n)
    if not hits:
        drop_ids.append(e['id'])
        o.write('🗑 id%d %s ＝組み直しに出てこない（雛形）\n' % (e['id'], (e.get('name') or '')[:36]))
        removed += 1
        continue
    keep = hits[0]
    used.add(id(keep))
    before = [t['type'] for t in e['tickets']]
    after = [t['type'] for t in keep['tickets']]
    if before != after:
        o.write('id%d %s ｜枠 %d→%d\n' % (e['id'], (e.get('name') or '')[:34], len(before), len(after)))
        for t in sorted(set(after) - set(before))[:4]:
            o.write('   ＋ %s\n' % t[:70])
        e['tickets'] = json.loads(json.dumps(keep['tickets']))
        e['name'] = keep['name']
        e['dateLabel'] = keep['dateLabel']
        e['venue'] = keep['venue']
        e['prefecture'] = keep['prefecture']
        e['date'] = keep['date']
        swapped += 1
    else:
        same += 1
    # 畳みすぎを解いた分＝2本目以降は新しいidで足す
    for n in hits[1:]:
        if id(n) in used:
            continue
        used.add(id(n))
        nid += 1
        add.append({'id': nid, **{k: v for k, v in n.items() if k != 'id' and not k.startswith('_merged')}})
        o.write('   ✂️畳みすぎを解いた → 新id%d %s\n' % (nid, n['name'][:34]))
        unfolded += 1

EVENTS = [e for e in EVENTS if e['id'] not in set(drop_ids)] + add
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
arr = [i for i in cur if i not in set(drop_ids)] + [e['id'] for e in add]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + '[' + ', '.join(map(str, arr)) + ']', h, count=1)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h2[:m2.start()] + m2.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m2.group(3) + h2[m2.end():])

pool = {e['id'] for e in EVENTS if e.get('genre') == 'new'}
o.write('\n差し替え %d / 畳みすぎを解いて追加 %d / 消した %d / そのまま %d\n'
        % (swapped, unfolded, removed, same))
o.write('EVENTS %d件 / 新着プール %d件 / NEW_ORDER %d件 / 一致=%s\n'
        % (len(EVENTS), len(pool), len(arr), pool == set(arr)))
o.close()
