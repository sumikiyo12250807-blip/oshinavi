# -*- coding: utf-8 -*-
# 11/22 18時のトレンド（SixTONES・大相撲の優勝決定戦・ジャパンカップ ほか）の名前で、いま買える枠があるか
import io, sys, json
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = io.open('C:/Users/user/oshinavi/tmp/x1122/x/trend_1123.txt', 'w', encoding='utf-8')
for k in ['SixTONES', '大相撲', 'ジャパンカップ', 'マイルCS', '夫婦']:
    hit = [e for e in E if e.get('genre') != 'new' and k in ((e.get('name') or '') + (e.get('artist') or ''))]
    out.write('##### %s %d件\n' % (k, len(hit)))
    for e in hit[:15]:
        ts = [t for t in e.get('tickets') or [] if (t.get('date') or '') >= '2026-11-22' and not t.get('soldout')]
        out.write('%s %s ｜ %s ｜ %s ｜ 買える枠%d %s\n' % (e['id'], e.get('genre'), (e.get('name') or '')[:50], e.get('date'), len(ts), [t.get('type')[:45] for t in ts[:3]]))
out.close()
print('ok')
