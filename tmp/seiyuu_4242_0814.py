# -*- coding: utf-8 -*-
"""id4242 神谷浩史に extraGenres:["seiyuu"] を足す。
ぴあのカテゴリは「音楽/J-POP・ROCK」なので主ジャンルは jpop のまま（ぴあが分けてないものを人が分けない
＝project_vendor_genre_autoassign）。ただし主役は声優なので、声優タブでも見つかるように両方持たせる
（feedback_genre_both_when_unclear）。既存の同型＝id3582 水瀬いのり＝jpop + extra seiyuu。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
for e in EV:
    if e.get('id') == 4242:
        e['extraGenres'] = ['seiyuu']
        print('id4242 genre=%s extra=%s  %s' % (e.get('genre'), e.get('extraGenres'), e.get('name')))
new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('→ 適用')
