# -*- coding: utf-8 -*-
"""実測で見つけた「発売前の枠を持つ未登録ページ」を rakuten_harvest の形で取り直して
build_rakuten_entries に渡せる候補ファイルにする。"""
import sys, os, json, io
os.chdir(r'C:\Users\user\oshinavi')
sys.path.insert(0, 'tools')
import rakuten_harvest as rh
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

URLS = [
    "https://ticket.rakuten.co.jp/music/jpop/rt4tkw2/",
    "https://ticket.rakuten.co.jp/music/jpop/rt4tkw3/",
    "https://ticket.rakuten.co.jp/music/jpop/rt4tkw1/",
    "https://ticket.rakuten.co.jp/music/rtkb710/",
    "https://ticket.rakuten.co.jp/event/rtyt103/",
]
out = []
for u in URLS:
    rec = rh.parse_page(u, rh.fetch(u))
    ok, why = rh.alive(rec)
    print('%-52s 公演%d / 枠%d / alive=%s %s'
          % (rec.get('name', '')[:40], len(rec.get('perfs') or []),
             len(rec.get('windows') or []), ok, why))
    for w in rec.get('windows') or []:
        print('      枠: %-24s %s' % ((w.get('type') or '')[:24], w.get('timming')))
    if ok:
        out.append(rec)
json.dump(out, io.open('tmp/rakuten_presale_cand_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n%d件を tmp/rakuten_presale_cand_0909.json に書いた' % len(out))
