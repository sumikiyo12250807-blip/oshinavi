# -*- coding: utf-8 -*-
# 11/23 16時台のトレンド（競馬＝東スポ杯・ホープフル・WIN5／#めめぐらむ／勤労感謝の日）の名前で、いま買える枠があるか
import io, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = io.open('C:/Users/user/oshinavi/tmp/x1123/x/trend_1124.txt', 'w', encoding='utf-8')
for k in ['競馬', 'JRA', 'ホープフル', '東スポ', '有馬', 'Snow Man', '目黒蓮', 'めめ', 'サメカツ']:
    hit = [e for e in E if e.get('genre') != 'new' and k in ((e.get('name') or '') + (e.get('artist') or ''))]
    out.write('##### %s %d件\n' % (k, len(hit)))
    for e in hit[:10]:
        ts = [t for t in e.get('tickets') or [] if (t.get('date') or '') >= '2026-11-23' and not t.get('soldout')]
        out.write('%s %s ｜ %s ｜ %s ｜ 買える枠%d %s\n' % (e['id'], e.get('genre'), (e.get('name') or '')[:50], e.get('date'), len(ts), [t.get('type')[:45] for t in ts[:3]]))
out.close()
