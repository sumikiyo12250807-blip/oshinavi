# -*- coding: utf-8 -*-
"""空カッコvenue4件を実会場名(半角)に修正。ぴあ個別ページで会場裏取り済。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
FIX = {
 2150: {"venue": "全国ツアー（SPIRITUAL LOUNGE／下北沢DaisyBar）"},
 2166: {"venue": "渋谷区文化総合センター大和田 さくらホール／日経ホール", "prefecture": "東京"},
 2190: {"venue": "全国ツアー（LIV LABO／Music Bar ドミナント）"},
 2194: {"venue": "小樽GOLDSTONE／ペニーレーン24", "prefecture": "北海道"},
}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    f = FIX.get(e.get('id'))
    if not f: continue
    e.update(f); n += 1
print(f"fixed {n}/{len(FIX)}")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0708_venue_fix','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0708_venue_fix)")
