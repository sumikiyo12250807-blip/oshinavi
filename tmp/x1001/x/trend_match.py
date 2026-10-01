# -*- coding: utf-8 -*-
"""Xトレンド8位まで（10/1 17:1x）の語を EVENTS（artist/name/venue）に当て、いま買える枠がある分だけ出す → trend_match.txt"""
import io, json, re
root = 'C:/Users/user/oshinavi/'
TODAY = '2026-10-01'
WORDS = ['ヴァンビ', '小園海斗', '小園', 'ハセシン', 'ZETA', '楽天モバイル', 'ファミマ', 'バウム', 'ロナルド', '首位打者', '伊東四朗', 'yogibo', 'Yogibo', '広島東洋カープ', 'カープ']
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
out = io.open(root + 'tmp/x1001/x/trend_match.txt', 'w', encoding='utf-8')
for w in WORDS:
    hits = []
    for e in E:
        if e.get('genre') == 'new':
            continue
        hay = ' '.join([e.get('artist') or '', e.get('name') or '', e.get('venue') or ''])
        if w.lower() in hay.lower():
            live = [t for t in e['tickets'] if (t.get('date') or '') >= TODAY and not t.get('soldout')]
            hits.append((e['id'], e.get('name'), e.get('date'), len(live), live[0]['type'] if live else ''))
    out.write('■ %s %d\n' % (w, len(hits)))
    for h in hits[:10]:
        out.write('    %s\n' % (h,))
