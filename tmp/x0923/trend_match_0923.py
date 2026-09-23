# -*- coding: utf-8 -*-
"""Xトレンド8位までの名前を index.html に当てて、いま買える枠があるかを見る（読むだけ・9/22夜）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
WORDS = ['SHOCK', 'ヴェスナ', 'Vesna', '乃木坂', '櫻坂', '日向坂', '坂道', '学園アイドルマスター', '学マス', '堂本光一', 'JCOM', 'ジェイコム']
h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
for w in WORDS:
    hits = [e for e in ev if w in (e.get('artist') or '') + (e.get('name') or '')]
    print('%s: %d' % (w, len(hits)))
    for e in hits[:5]:
        live = [t for t in e.get('tickets') or [] if not t.get('soldOut') and not t.get('saleEnded')]
        print('   id%s %s | %s | 枠%d 生き%d' % (e['id'], e.get('artist'), e.get('dateLabel'), len(e.get('tickets') or []), len(live)))
