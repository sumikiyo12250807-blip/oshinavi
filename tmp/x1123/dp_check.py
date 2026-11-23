# -*- coding: utf-8 -*-
import io, sys, re
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
t = io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read()
E = C.load(t)
o = io.open('C:/Users/user/oshinavi/tmp/x1123/dp_check.txt', 'w', encoding='utf-8')
rows = [(e['id'], e.get('artist'), e['links'].get('amazonDp'), e['links'].get('amazonDpTitle')) for e in E if (e.get('links') or {}).get('amazonDp')]
for r in rows:
    o.write('id%s %s → %s ｜ %s\n' % r)
o.write('計 %d枚\n' % len(rows))
o.write('画面の差し替え入り=%s 宿の帯入り=%s\n' % ('ev.links.amazonDp ? ev.links.amazonDp' in t, 'class="hotel-strip"' in t))
