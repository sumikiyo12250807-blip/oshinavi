# -*- coding: utf-8 -*-
# 同じ型（B.LEAGUE のシーズンシート等＝試合の無い日の「販売用」イベントを試合として載せている）がほかにあるか
import io, re, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
out = io.open('C:/Users/user/oshinavi/tmp/x1124/spot/season.txt', 'w', encoding='utf-8')
n = 0
for e in E:
    s = (e.get('name') or '') + ' ' + ' '.join(t.get('type') or '' for t in e.get('tickets') or [])
    if re.search(r'シーズンシート|シーズンパス|年間シート|シーズンチケット|販売用', s) or re.search(r'^(.+?)／\1$', e.get('artist') or ''):
        n += 1
        out.write('%d %s ｜%s ｜%s ｜%s\n' % (e['id'], e.get('genre'), e.get('artist'), e.get('name'), e.get('dateLabel')))
out.write('計 %d\n' % n)
