# -*- coding: utf-8 -*-
"""TIGETの新規を新着プール（genre:"new"）に投入する。
🚨撮影会／駐車券だけ／参加エントリーフォームの5件はよける（載せた前例が無く、ユーザーに聞いている件）。
   id は本番の番号＝いまの最大idと last_batch の最大 id_to の次から。削除済みidは再利用しない。
"""
import re, json, io

HOLD = re.compile(r'撮影会|チェキ撮影|駐車|エントリーフォーム|参加エントリ')

new = json.load(open('tmp/tiget_new_0918.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
lb = json.load(open('.claude/state/last_batch.json', encoding='utf-8'))['batches']
nid = max([e['id'] for e in EVENTS] + [b.get('id_to') or 0 for b in lb])

put, hold = [], []
for e in sorted(new, key=lambda x: x['date']):
    (hold if HOLD.search(e['name']) else put).append(e)

for e in put:
    nid += 1
    e['id'] = nid                      # 報告に出すので元の dict にも入れる
    e2 = {'id': nid}
    e2.update({k: v for k, v in e.items() if k != 'id' and not k.startswith('_merged')})
    EVENTS.append(e2)

mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
ids = [e['id'] for e in EVENTS if e.get('genre') == 'new' and e['id'] not in cur]
merged = cur + sorted(i for i in ids)
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            r'\g<1>' + '[' + ', '.join(str(i) for i in merged) + ']', h, count=1)
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h2[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h2[m.end():])

o = io.open('tmp/tiget_inject_0918.txt', 'w', encoding='utf-8')
o.write(f"投入 {len(put)}件 id{put[0]['id'] if put else '-'}..{put[-1]['id'] if put else '-'} / よけた {len(hold)}件\n")
o.write(f"EVENTS {len(EVENTS)}件 / NEW_ORDER {len(merged)}件\n\n--- よけた（ユーザーに聞く）---\n")
for e in hold:
    o.write(f"  {e['name'][:52]} 公演{e['date']} {e['venue'][:26]}\n    {e['links']['tiget']}\n")
o.write('\n--- 投入した ---\n')
for e in put:
    o.write(f"id{e['id']}\t{e['_genre']}\t{e['name'][:44]}\t{e['dateLabel'][:30]}\t{e['venue'][:22]}\t枠{len(e['tickets'])}\n")
o.close()
print('投入', len(put), 'よけた', len(hold), 'EVENTS', len(EVENTS), 'NEW_ORDER', len(merged))
