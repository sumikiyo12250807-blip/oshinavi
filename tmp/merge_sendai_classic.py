# -*- coding: utf-8 -*-
"""仙台クラシックフェスティバル2026 の3件(1947/1948/1949=10/2,10/3,10/4公演)を
1エントリ(id1947)に統合。同一フェス・同一会場・全部7/12 10:00発売の発売前。
日別3チケット(各日の個別bundle url付き)。1948/1949はEVENTS/NEW_ORDER両方から除去。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

DAY_URL = {
    1947: 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668980',  # 10/2
    1948: 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668981',  # 10/3
    1949: 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668982',  # 10/4
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

base = byid[1947]
# 3件のチケットを日別url付きで束ねる
tickets = []
for i in (1947, 1948, 1949):
    for t in byid[i].get('tickets', []):
        nt = dict(t)
        nt['url'] = DAY_URL[i]
        tickets.append(nt)

base['artist'] = '仙台クラシックフェスティバル2026'
base['name'] = '仙台クラシックフェスティバル2026'
base['date'] = '2026-10-04'  # 千秋楽
base['dateLabel'] = '2026年10月2日(金)〜2026年10月4日(日) 宮城'
base['tickets'] = tickets

print("統合後 id1947:")
print("  artist=", base['artist'])
print("  dateLabel=", base['dateLabel'], "date=", base['date'])
for t in tickets:
    print("   ticket:", t.get('type'), "| url=", t.get('url'))

# 1948/1949 除去
kept = [e for e in EVENTS if e['id'] not in (1948, 1949)]
print(f"件数 {len(EVENTS)} -> {len(kept)}")

# NEW_ORDER から 1948/1949 除去
mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', h)
order = json.loads(mo.group(2))
order2 = [x for x in order if x not in (1948, 1949)]
print(f"NEW_ORDER {len(order)} -> {len(order2)}")

if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    new_order = json.dumps(order2)
    open('index.html.bak_0704_merge_sendai', 'w', encoding='utf-8').write(h)
    h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    # NEW_ORDER置換(EVENTS書換後の文字列で再検索)
    mo2 = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', h2)
    h2 = h2[:mo2.start()] + mo2.group(1) + new_order + mo2.group(3) + h2[mo2.end():]
    open('index.html', 'w', encoding='utf-8').write(h2)
    print("✅ 統合完了 (backup: index.html.bak_0704_merge_sendai)")
