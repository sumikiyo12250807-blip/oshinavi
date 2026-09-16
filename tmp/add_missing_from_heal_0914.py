# -*- coding: utf-8 -*-
"""取り直し（tmp/heal_ids.json）のうち、いまの登録に無い公演の枠だけを足す（置き換えない）（2026-09-14 朝）。
対象＝727 西村由紀江（宮城12/13 プリセール）／5332 人間椅子（宮城の先行）／7326 35.7（宮城11/15 プレリザーブ）。
heal の --apply は丸ごと置き換えるので、今朝よそのページ（ticket.pia.jp の eventCd）から足した枠が取り直しに入らず、
安全弁が「生きた枠が消える」と止めた。→ 置き換えずに「いまの登録に無い骨格（券種名＋（…公演））」だけ足す。
🚨足す枠には必ずURLを焼き込む（取り直しの枠がURLを持たない時は、そのエントリの links.pia）。
使い方: python tmp/add_missing_from_heal_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
IDS = [727, 5332, 7326]
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}


def head(ty):
    ty = re.sub(r'^[「」『』]?', '', ty or '')
    m = re.match(r'^(.*?（[^（）]*公演）)', ty)
    return m.group(1) if m else ty


src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
n = 0
for i in IDS:
    e, b = by[i], built.get(i)
    if not b:
        print('id%s 取り直しが無い' % i)
        continue
    have = {head(t.get('type')) for t in e.get('tickets') or []}
    for t in b.get('tickets') or []:
        if head(t.get('type')) in have:
            continue
        nt = dict(t)
        nt['url'] = t.get('url') or (e.get('links') or {}).get('pia') or ''
        assert nt['url'], 'URL の無い枠は足さない'
        e['tickets'].append(nt)
        n += 1
        print('id%-5s + %s | date=%s | %s' % (i, nt['type'], nt.get('date'), nt['url']))
print('足した枠 %d' % n)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了')
