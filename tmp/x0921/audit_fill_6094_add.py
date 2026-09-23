# -*- coding: utf-8 -*-
"""id6094 新しい学校のリーダーズ：照合で見つかった大阪・愛知の受付中の枠を足す（1URLずつ機械パースした結果から）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
b = json.load(io.open('tmp/x0921/audit_fill_6094b.json', encoding='utf-8'))
h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
e = [x for x in EV if x['id'] == 6094][0]
have = {(t.get('type'), t.get('url')) for t in e['tickets']}
for s in b:
    for t in s['tickets']:
        t = dict(t); t.setdefault('url', s['links']['pia'])
        if (t['type'], t['url']) in have:
            continue
        e['tickets'].append(t); print('足し込み', t['type'], t['url'])
if '--apply' in sys.argv:
    arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
    io.open(P, 'w', encoding='utf-8', newline='').write(h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
    print('書き込み完了')
