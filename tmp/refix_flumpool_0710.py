# -*- coding: utf-8 -*-
"""id=2311 flumpool: 福岡10/17・大阪9/12のプレリザーブ取りこぼし（ユーザー指摘）。
reconcile「登録2枠/ぴあ買える4枠」。ぴあbundleから再パースして全枠取り込む。
[[feedback_deadline_extended_after_register]]（登録後にぴあが枠を足す）"""
import re, json, sys, io
sys.path.insert(0, 'tools')
from build_pia_entries import build
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BUNDLE = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2666817'
ne = build({'newid': 2311, 'artist': 'flumpool', 'urls': [BUNDLE]})
if ne is None:
    out.write('買える枠ゼロ\n'); out.flush(); sys.exit(0)
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
ev = next(e for e in EVENTS if e['id'] == 2311)
ev['tickets'] = ne['tickets']
ev['venue'] = ne['venue']
ev['prefecture'] = ne['prefecture']
ev['date'] = ne['date']
ev['dateLabel'] = ne['dateLabel']
out.write(f"venue: {ev['venue']}\ndate: {ev['date']}\ntickets {len(ev['tickets'])}枠:\n")
for t in ev['tickets']:
    out.write(f"   {t.get('startDate')} -> {t.get('date')} | {t.get('type')}\n")
out.flush()
if '--apply' not in sys.argv:
    out.write('(DRY)\n'); out.flush(); sys.exit(0)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0710_flumpool','w',encoding='utf-8').write(idx)
open('index.html','w',encoding='utf-8').write(idx[:m.start()]+m.group(1)+new_arr+m.group(3)+idx[m.end():])
out.write('written\n'); out.flush()
