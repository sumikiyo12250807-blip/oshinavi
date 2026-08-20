# -*- coding: utf-8 -*-
"""id=4639 二胡とピアノでめぐる名曲の旅 を yougaku → classic に直す（2026-08-19 ユーザー判断）。
ぴあのカテゴリは「音楽/民族音楽」で、登録ツールの対応表では yougaku（海外の音楽の受け皿）に倒れるが、
中身は二胡とピアノでクラシックの名曲を弾く公演。ユーザーが classic を選んだ。
⚠️ PIA_GENRE_MAP の「民族音楽→yougaku」自体は変えない（過去に「ネパールの詩心」で決めた判断があるため。
   この1件だけの上書き＝単独ケースを他に巻き込まない）。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    if e['id'] != 4639:
        continue
    print('%s: %s → classic' % (e['name'], e.get('genre')))
    e['genre'] = 'classic'
    n += 1

if n:
    shutil.copyfile('index.html', 'index.html.bak_0819_4639')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 更新 ===' % n)
