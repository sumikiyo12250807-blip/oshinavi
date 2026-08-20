# -*- coding: utf-8 -*-
"""2371 シルバニアファミリー展40th の救済投入。
build_inject 時に落ちたがフェッチのゆらぎだった（単体再buildで6枠取得成功）。
前売券3種/当日券3種は表示文言が重複するので意図集約して4枠にする。"""
import re, json, sys, io
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import build

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2666690'
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
newid = max(e['id'] for e in EVENTS) + 1

ne = build({'newid': newid, 'artist': 'シルバニアファミリー展40th', 'urls': [URL]})
if ne is None:
    print('買える枠ゼロ→投入しない'); sys.exit(0)

# 同一(type,date,startDate)の重複券種を集約
seen, uniq = set(), []
for t in ne['tickets']:
    k = (t.get('type'), t.get('date'), t.get('startDate'))
    if k in seen: continue
    seen.add(k); uniq.append(t)
ne['tickets'] = uniq
ne['genre'] = 'new'
print(f"id={newid} {ne['name']} @ {ne['venue']}（{ne['prefecture']}）公演日 {ne['date']}")
for t in ne['tickets']:
    print('   ', t.get('startDate'), '->', t.get('date'), '|', t.get('type'))

if '--apply' not in sys.argv:
    print('(DRY)'); sys.exit(0)
EVENTS.append(ne)
out = idx[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + idx[m.end():]
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
cur = [x.strip() for x in mo.group(1).split(',') if x.strip()] + [str(newid)]
out = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[' + ', '.join(cur) + r']\2', out, count=1)
open('index.html.bak_0710_silvania', 'w', encoding='utf-8').write(idx)
open('index.html', 'w', encoding='utf-8').write(out)
print(f'投入 / NEW_ORDER {len(cur)}件')
