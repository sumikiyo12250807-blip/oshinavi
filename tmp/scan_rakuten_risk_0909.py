# -*- coding: utf-8 -*-
"""card_end 流用の疑いがある楽天枠を、ジャンル別に数える。
   「会期券（展覧会・水族館など会期中ずっと同じ券）」と「別々の公演（ツアー・試合）」は
   同じ形でも意味が違うので、ジャンルで当たりを付ける。"""
import io, re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

def rakuten_slot(t, e):
    u = (t.get('url') or '') or json.dumps(e.get('links') or {}, ensure_ascii=False)
    return 'rakuten' in u

KIKAN = {'art', 'event', 'gourmet', 'kids'}   # 会期券になりがち
rows = []
for e in EV:
    for t in e.get('tickets') or []:
        if not rakuten_slot(t, e) or t.get('soldout') or t.get('saleUntilSoldOut') or t.get('saleEndUnknown'):
            continue
        ty = t.get('type') or ''
        m = re.search(r'（([^（）]*?)公演）', ty)
        inner = m.group(1) if m else ''
        if not ('〜' in inner or '～' in inner):
            continue                       # 複数日にまたがる枠だけ見る
        rows.append((e.get('genre') or '?', e['id'], (e.get('name') or '')[:30], t.get('date')))

c = collections.Counter(g for g, *_ in rows)
print('複数日を1枠にまとめた楽天枠 = %d件' % len(rows))
print()
print('%-12s %-5s %s' % ('ジャンル', '件数', '性格'))
for g, n in c.most_common():
    kind = '会期券かも（正しい可能性）' if g in KIKAN else '🚨別々の公演＝締切が嘘になりやすい'
    print('%-12s %-5d %s' % (g, n, kind))
risky = [r for r in rows if r[0] not in KIKAN]
print()
print('🚨危ない側（別々の公演）= %d件' % len(risky))
for g, i, name, d in risky[:30]:
    print('   id%-6d [%-9s] %-32s 締切=%s' % (i, g, name, d))
if len(risky) > 30:
    print('   … 他 %d件' % (len(risky) - 30))
