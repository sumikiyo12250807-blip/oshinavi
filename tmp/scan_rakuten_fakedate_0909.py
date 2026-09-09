# -*- coding: utf-8 -*-
"""楽天由来の枠で「締切に公演日を流用した疑い」を全部洗い出す。
   疑いの型＝枠の date が、その枠の券種名に書かれた公演日／エントリの公演日と一致する。"""
import io, re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

def rakuten_slot(t, e):
    u = (t.get('url') or '') or json.dumps(e.get('links') or {}, ensure_ascii=False)
    return 'rakuten' in u

rows = []
tot = 0
for e in EV:
    for t in e.get('tickets') or []:
        if not rakuten_slot(t, e):
            continue
        tot += 1
        if t.get('soldout') or t.get('saleUntilSoldOut') or t.get('saleEndUnknown'):
            continue
        d = t.get('date') or ''
        ed = e.get('date') or ''
        # 券種名の末尾に「〜M/D」形の締切が書いてあるか
        has_end = bool(re.search(r'〜\s*(?:R\d+年 )?\d{1,2}/\d{1,2}', t.get('type') or ''))
        if d and d == ed:
            rows.append((e['id'], (e.get('name') or '')[:30], d, ed, has_end,
                         (t.get('type') or '')[:56]))

print('楽天由来の枠 %d件 / うち「締切＝エントリの公演日」= %d件' % (tot, len(rows)))
print()
for i, name, d, ed, has_end, ty in rows:
    print('id%-6d %-32s 締切=%s 公演日=%s' % (i, name, d, ed))
    print('        %s' % ty)
