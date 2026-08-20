# -*- coding: utf-8 -*-
"""新着プール(genre:new)の内訳レポート：下書きジャンル分布・_piaSub空の子・発売日"""
import io, json, re, collections, datetime

TODAY = datetime.date.today()
raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
arr = json.loads(m.group(1))
new = [e for e in arr if e.get('genre') == 'new']

out = ['新着プール %d件 (id %s..%s)' % (len(new), new[0]['id'], new[-1]['id'])]

g = collections.Counter(e.get('_genre') or '(空)' for e in new)
out.append('■下書きジャンル: %s' % json.dumps(dict(g), ensure_ascii=False))

blank = [e for e in new if not e.get('_genre') or e.get('_genre') in ('', 'その他')]
out.append('■下書きが空/その他 %d件（振り分け時に人の判断が必要）' % len(blank))
for e in blank:
    out.append('   id=%s %s | _piaSub=%r' % (e['id'], e.get('name'), e.get('_piaSub')))

nosub = [e for e in new if not e.get('_piaSub')]
out.append('■_piaSub 空 %d件' % len(nosub))
for e in nosub:
    out.append('   id=%s %s' % (e['id'], e.get('name')))

# 発売開始までの日数分布
buck = collections.Counter()
for e in new:
    ds = [t.get('startDate') for t in e.get('tickets', []) if t.get('startDate')]
    if not ds:
        buck['販売中のみ'] += 1
        continue
    d0 = min(ds)
    n = (datetime.date(*[int(x) for x in d0.split('-')]) - TODAY).days
    buck['4日以上先' if n >= 4 else ('2〜3日後' if n >= 2 else ('明日' if n == 1 else '本日/過去'))] += 1
out.append('■発売開始まで: %s' % json.dumps(dict(buck), ensure_ascii=False))

io.open('tmp/out_newpool_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_newpool_0730.txt')
