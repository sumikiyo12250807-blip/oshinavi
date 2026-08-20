# -*- coding: utf-8 -*-
"""楽天候補 vs 既存DB を前方一致・部分一致で突合（二重登録の罠つぶし）。"""
import sys, re, json, unicodedata
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

rows = json.load(open('tmp/rakuten_cand_0725.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

def key(s):
    return R.norm_name(s)

db = []
for e in EV:
    for f in ('name', 'artist'):
        k = key(e.get(f))
        if k:
            db.append((k, e))

dup, fresh = [], []
for r in rows:
    k = key(r['name'])
    hit = None
    for dk, e in db:
        if not dk or len(dk) < 5:
            continue
        # 前方一致どちらか（楽天は「〜〜〜［東京］」「〜〜〜 新世代ヒーロー…」と長い/短い両方ある）
        if k.startswith(dk[:12]) or dk.startswith(k[:12]):
            hit = e
            break
    (dup if hit else fresh).append((r, hit))

print('=== 既存とかぶり %d件（新規追加でなく既存への枠追加を検討）===' % len(dup))
for r, e in dup:
    print('  楽天: %s' % r['name'][:46])
    print('     ↔ 既存 id=%s %s (genre=%s)' % (e.get('id'), (e.get('name') or '')[:40], e.get('genre')))

print('\n=== 新規 %d件 ===' % len(fresh))
for r, _ in fresh:
    print('  %-46s genre=%s' % (r['name'][:46], r['_genre'] or '-'))

json.dump([r for r, _ in fresh], open('tmp/rakuten_fresh.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([{'rakuten': r['name'], 'url': r['url'], 'exist_id': e.get('id'), 'exist_name': e.get('name')} for r, e in dup],
          open('tmp/rakuten_dup.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n→ tmp/rakuten_fresh.json / tmp/rakuten_dup.json')
