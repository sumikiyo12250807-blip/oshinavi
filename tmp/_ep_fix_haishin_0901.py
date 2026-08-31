# -*- coding: utf-8 -*-
"""e+の配信(Streaming+)枠が「県が空」のまま「（ 11/22公演）」と出るのを直す。
実ページで Streaming+／アーカイブ表記を確認済み（2026-09-01）。
表記は既存の慣例に合わせる＝券種名に【動画配信】、県は「全国」。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    (6061, 'https://eplus.jp/sf/detail/4531630001-P0030001P021001', '2026-11-22'):
        '先着一般発売【動画配信】（全国 11/16公演）10/1 10:00発売',
    (6067, 'https://eplus.jp/sf/detail/4125060001-P0030013P021001', '2026-11-22'):
        '先着受付【動画配信】（全国 11/22公演）9/14 11:00発売',
    (6067, 'https://eplus.jp/sf/detail/4125060001-P0030013P021001', '2026-11-28'):
        '先着受付【動画配信】【アーカイブ】（全国 11/22公演）9/14 11:00発売',
}
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    for t in e.get('tickets', []):
        k = (e.get('id'), t.get('url'), t.get('date'))
        if k in FIX:
            print(f"id{e['id']}\n  旧 {t['type']}\n  新 {FIX[k]}")
            t['type'] = FIX[k]; n += 1
NL = '\r\n' if '\r\n' in src else '\n'
open(f'index.html.bak_{datetime.date.today():%m%d}_haishin', 'w', encoding='utf-8', newline='').write(src)
body = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print(f'✅ {n}枠を修正')
