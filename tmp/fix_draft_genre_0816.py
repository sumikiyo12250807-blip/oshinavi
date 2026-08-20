# -*- coding: utf-8 -*-
"""新着プールの _genre 下書きのうち、ぴあがカテゴリを返さず名前fallbackで engeki になった子を主役で読み直す。
（project_vendor_genre_autoassign＝ぴあが音楽カテゴリを付けている限りそのまま。ここは"ぴあが付けていない"ケース）
genre は "new" のまま触らない＝振り分けはユーザーの合図待ち。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    4326: ('jpop', 'ぴあがカテゴリ無し(bundle)。Kis-My-Ft2＝J-POP'),
    4329: ('jpop', 'ぴあがカテゴリ無し(bundle)。NEE＝バンドだがJ-POP・ROCK一括りの約束'),
    4356: ('jpop', 'ぴあは「イベント/学園祭」だが主役はロックバンドのドミコ'),
    4360: ('anime', 'ぴあは「イベント/イベントその他」だがTVアニメのイベント'),
    4373: ('jpop', 'ぴあがカテゴリ無し(bundle)。椎名林檎＝J-POP'),
}

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

n = 0
for e in EVENTS:
    f = FIX.get(e.get('id'))
    if not f or e.get('genre') != 'new':
        continue
    print("id%s %s → %s  （%s）" % (e['id'], e.get('_genre'), f[0], f[1]))
    e['_genre'] = f[0]; n += 1

if not n:
    print("変更なし"); sys.exit(0)

bak = 'index.html.bak_0816_draftgenre'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + h[m.end():])
print("=== %d件 適用 ===" % n)
