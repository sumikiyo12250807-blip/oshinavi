# -*- coding: utf-8 -*-
"""id=611 の見出し情報をぴあ再導出に合わせる（ticketsは適用済み）。CRLFはテキストモード書きで維持。"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    611: {
        "date": "2026-09-19",
        "dateLabel": "2026年8月23日(日)〜2026年9月19日(土) 東京・大阪",
        "venue": "全国ツアー（WWW X／恵比寿ザ・ガーデンホール／OSAKA MUSE）",
        "prefecture": "東京・大阪",
    },
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

changed = 0
for e in EVENTS:
    f = FIX.get(e.get('id'))
    if not f:
        continue
    for k, v in f.items():
        if e.get(k) != v:
            print("id=%s %-11s %s → %s" % (e['id'], k, e.get(k), v))
            e[k] = v; changed += 1

if not changed:
    print("変更なし"); sys.exit(0)

bak = 'index.html.bak_0816_meta2'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("=== %d項目 適用 ===" % changed)
