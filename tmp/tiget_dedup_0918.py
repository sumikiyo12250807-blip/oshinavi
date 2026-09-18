# -*- coding: utf-8 -*-
# TIGETの組み上がりを登録と突き合わせる。①TIGETのURL ②正規化した名前×公演日
import re, json, io, unicodedata

b = json.load(open('tmp/built_tiget_0918.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


have_urls = set(re.findall(r'tiget\.net/events/(\d+)', h))
namedate = set()
by_name = {}
for e in ev:
    n = norm(e.get('artist') or e.get('name'))
    n2 = norm(e.get('name'))
    by_name.setdefault(n, []).append(e)
    if n2 != n:
        by_name.setdefault(n2, []).append(e)
    days = set(re.findall(r'\d{4}-\d{2}-\d{2}', json.dumps(e, ensure_ascii=False)))
    for d in days:
        namedate.add((n, d))
        namedate.add((n2, d))

o = io.open('tmp/tiget_dedup_0918.txt', 'w', encoding='utf-8')
new, dup, maybe = [], [], []
for e in b['entries']:
    urls = [e['links']['tiget']] + (e.get('_merged_from') or [])
    ids = {m for u in urls for m in re.findall(r'/events/(\d+)', u)}
    if ids & have_urls:
        dup.append((e, 'TIGETのURLが既に登録にある %s' % sorted(ids & have_urls)))
        continue
    n, n2 = norm(e['artist']), norm(e['name'])
    if (n, e['date']) in namedate or (n2, e['date']) in namedate:
        maybe.append((e, '名前×公演日が登録と一致'))
        continue
    hits = (by_name.get(n) or []) + (by_name.get(n2) or [])
    if hits:
        maybe.append((e, '同名の登録あり id%s' % sorted({x['id'] for x in hits})))
        continue
    new.append(e)

o.write(f"組み上がり {len(b['entries'])}件 → 新規 {len(new)} / URL重複 {len(dup)} / ⚠️要確認 {len(maybe)}\n")
for lbl, rows in (('--- URLが既にある（入れない）---', dup), ('--- ⚠️要確認 ---', maybe)):
    o.write('\n' + lbl + '\n')
    for e, why in rows:
        o.write(f"  {e['name'][:44]} 公演{e['date']} … {why}\n    {e['links']['tiget']}\n")
o.write('\n--- 新規 ---\n')
for e in new:
    o.write(f"  {e['_genre']}\t{e['name'][:46]}\t{e['dateLabel'][:34]}\t{e['venue'][:24]}\t枠{len(e['tickets'])}\n")
o.close()
json.dump(new, io.open('tmp/tiget_new_0918.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規', len(new), 'URL重複', len(dup), '要確認', len(maybe))
