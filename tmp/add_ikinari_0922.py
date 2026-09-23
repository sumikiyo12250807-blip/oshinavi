# -*- coding: utf-8 -*-
"""id1149 いぎなり東北産に、抜けていたゼビオアリーナ仙台（eventCd=2633498・抽選受付中）の枠を足し算で足す。
取り直しは build_pia_entries.build（ぴあ実ページ）。元の枠は消さない。飛び先が空の枠にはそのURLを焼き込む。"""
import io, json, re, sys
sys.path.insert(0, 'tools')
import build_pia_entries as B
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2633498'
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 1149)
ne = B.build({'newid': 1149, 'artist': e['artist'], 'urls': [URL]})
have = {t['type'] for t in e['tickets']}
add = []
for t in (ne or {}).get('tickets') or []:
    if not t.get('url'):
        t['url'] = URL
    if t['type'] not in have:
        add.append(t)
for t in add:
    print('+', t['type'], '|', t.get('startDate'), t['date'], t.get('url'))
print('ぴあの取り直し: 公演日', (ne or {}).get('date'), '会場', (ne or {}).get('venue'))
if '--apply' in sys.argv and add:
    e['tickets'] += add
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
    print('書き込み完了', len(add))
