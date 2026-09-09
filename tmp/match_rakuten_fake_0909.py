# -*- coding: utf-8 -*-
"""実ページで「終わりが書かれていない」枠と、登録の枠を突き合わせて、
   **嘘の締切が付いている枠**だけを name で特定する。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

audit = json.load(io.open('tmp/rakuten_ends_0909.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}


def norm(s):
    return re.sub(r'\s+', '', s or '')


bad = []
for r in audit:
    noend = set(norm(x) for x in (r.get('終わりが書かれていない枠') or []))
    if not noend:
        continue
    for eid in r['ids']:
        e = EV.get(eid)
        if not e:
            continue
        for t in e.get('tickets') or []:
            if t.get('saleEndUnknown') or t.get('soldout') or t.get('saleUntilSoldOut'):
                continue
            ty = t.get('type') or ''
            head = norm(ty.split('（')[0])          # 券種名の頭＝枠名
            if head in noend and t.get('date'):
                bad.append((eid, (e.get('name') or '')[:32], ty[:58], t.get('date'), r['url']))

print('🚨実ページに終わりが無いのに締切を付けている枠 = %d件' % len(bad))
print()
for eid, name, ty, d, u in bad:
    print('id%-6d %-34s 締切=%s' % (eid, name, d))
    print('        %s' % ty)
json.dump([{'id': b[0], 'type': b[2], 'date': b[3], 'url': b[4]} for b in bad],
          io.open('tmp/rakuten_fake_ends_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
