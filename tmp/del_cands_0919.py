# 9/19 朝 期限切れ候補（開催終了＋全販売終了）の中身を並べる＝削除前の自己点検用
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
txt = open('tmp/expired_0919.txt', encoding='utf-8').read()
ids = [int(m) for m in re.findall(r'^  id=(\d+):.*\[全販売終了, 開催終了', txt, re.M)]
sys.path.insert(0, 'tools')
html = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', html, re.S)
events = json.loads(m.group(1))
byid = {e['id']: e for e in events}
flags = []
out = []
for i in ids:
    e = byid[i]
    ts = e.get('tickets', [])
    warn = []
    for t in ts:
        if t.get('saleUntilSoldOut'): warn.append('saleUntilSoldOut')
        if t.get('saleEndUnknown'): warn.append('saleEndUnknown')
        if t.get('date', '') >= '2026-09-19': warn.append('枠締切が今日以降:' + t.get('date', ''))
        for md in re.findall(r'(\d{1,2})/(\d{1,2})公演', t.get('type', '') + t.get('dateLabel', '')):
            mm, dd = int(md[0]), int(md[1])
            if (mm, dd) > (9, 18) and mm >= 9: warn.append(f'公演{mm}/{dd}')
        if 'R9' in t.get('type', ''): warn.append('R9')
    for k in ('endDate', 'lastDate'):
        if e.get(k, '') and e[k] >= '2026-09-19': warn.append(f'{k}={e[k]}')
    urls = [t.get('url') for t in ts if t.get('url')] or [e.get('link') or e.get('url')]
    out.append({'id': i, 'name': e.get('name') or e.get('title'), 'date': e.get('date'), 'venue': e.get('venue'), 'url': urls[0], 'warn': sorted(set(warn))})
    if warn: flags.append(i)
json.dump(out, open('tmp/del_cands_0919.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('候補', len(ids), '件 / 警告あり', len(flags), '件')
for o in out:
    if o['warn']: print(o['id'], o['name'], o['date'], o['warn'])
print(','.join(map(str, ids)))
