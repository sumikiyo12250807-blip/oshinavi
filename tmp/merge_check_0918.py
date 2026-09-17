# -*- coding: utf-8 -*-
# 投入前に「既存の同名エントリ」を探す（2026-08-18に39件が分裂していた事故の予防）
import re, json, io, unicodedata

built = json.load(open('tmp/built_ps0918_all.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\']', '', s)


idx = {}
for e in ev:
    idx.setdefault(norm(e.get('artist') or e.get('name')), []).append(e)

o = io.open('tmp/merge_check_0918.txt', 'w', encoding='utf-8')
same, newone = [], []
for b in built:
    n = norm(b.get('artist') or b.get('name'))
    hits = idx.get(n) or []
    if hits:
        same.append((b, hits))
    else:
        newone.append(b)
o.write(f"組み上がり {len(built)}件 → 既存に同名あり {len(same)}件 / 新規 {len(newone)}件\n")
o.write("\n=== 既存に同名あり（畳む候補）===\n")
for b, hits in same:
    o.write(f"id{b['id']} {b.get('artist','')[:44]} 公演{b.get('date')}\n")
    for e in hits:
        o.write(f"   → 既存 id{e['id']} genre={e.get('genre')} 公演{e.get('date')} {e.get('venue','')[:30]}\n")
o.write("\n=== 新規 ===\n")
for b in newone:
    o.write(f"id{b['id']}\t{b.get('artist','')[:48]}\t公演{b.get('date')}\t{b.get('venue','')[:26]}\t{b.get('_genre') or b.get('genre')}\n")
o.close()
print('same', len(same), 'new', len(newone))
