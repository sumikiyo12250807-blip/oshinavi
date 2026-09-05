# -*- coding: utf-8 -*-
"""id5784 ORCALAND に焼き込んだ e+ の個別URL 4本を外す（2026-09-05）。

理由＝この4枠は**ぴあ由来のラベル（〜9/10 23:59 等）**で、飛び先だけ e+ にすると
**バッジの締切（23:59）と実ページの締切（18:00）が食い違う**。
reconcile_eplus が [b-締切時刻ズレ] として正しく弾いた。

「url が空なら焼き込む」は [[feedback_tour_per_ticket_url]] の趣旨だけど、
**同じ売り場から取ったラベルにだけ**当てはまる。売り場が違う枠に他社のURLを付けると、
押した先の締切が違う＝[[feedback_no_fake_info]] になる。カード共通リンク（links.pia）に戻す。

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, io, re

PATH = 'index.html'
h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

e = by[5784]
n = 0
for t in e['tickets']:
    if t.get('type', '').startswith('一般発売（') and 'eplus.jp' in (t.get('url') or ''):
        del t['url']
        n += 1
assert n == 4, n

bak = 'index.html.bak_0905_revert5784'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('id5784 removed %d burned urls (backup %s)' % (n, bak))
