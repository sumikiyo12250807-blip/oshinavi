# -*- coding: utf-8 -*-
# 神保町マンゲキ（よしもと神保町漫才劇場）のお笑いライブのカードを数える → find_mangeki.txt
import io, json, re, collections
root = 'C:/Users/user/oshinavi/'
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
hit = [e for e in E if re.search(r'神保町漫才劇場|神保町マンゲキ|神保町よしもと', (e.get('venue') or '') + (e.get('name') or ''))]
out = io.open(root + 'tmp/x1001/find_mangeki.txt', 'w', encoding='utf-8')
out.write('%d件\n' % len(hit))
c = collections.Counter(e.get('name') for e in hit)
out.write('名前の種類 %d\n' % len(c))
for n, k in c.most_common(40):
    out.write('  %3d %s\n' % (k, n))
out.write('\n例:\n')
for e in hit[:8]:
    out.write(f"{e['id']} [{e.get('genre')}] {e.get('artist')} | {e.get('name')} | {e.get('venue')} | {e.get('dateLabel')} | 枠{len(e['tickets'])} {e['tickets'][0].get('url') if e['tickets'] else ''}\n")
    for t in e['tickets'][:3]:
        out.write(f"     {t.get('type')} | {t.get('startDate')}〜{t.get('date')}\n")
