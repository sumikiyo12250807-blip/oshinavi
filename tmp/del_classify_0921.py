# -*- coding: utf-8 -*-
"""公演が終わったエントリ（date < today）を売り場別・日付別に分類して一覧を出す。
DELETE_GATE.md 1.「公演が終わった＝消す（当日は残して翌朝）」に当たる分だけを機械で数える。
配信アーカイブ等で「公演終了だが買える枠あり」は別に出す（消さない）。
"""
import io, json, re, collections, datetime

TODAY = '2026-09-21'
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
ev = json.loads(m.group(1))


def vendor(e):
    ls = e.get('links') or {}
    for k in ('pia', 'tiget', 'eplus', 'rakuten', 'lawson'):
        if ls.get(k):
            return k
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        for k, pat in (('pia', 't.pia.jp'), ('tiget', 'tiget.net'),
                       ('eplus', 'eplus.jp'), ('rakuten', 'rakuten'),
                       ('lawson', 'l-tike')):
            if pat in u:
                return k
    return 'なし'


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


past, alive, byvendor, byday = [], [], collections.Counter(), collections.Counter()
for e in ev:
    d = e.get('date') or ''
    if not d or d >= TODAY:
        continue
    v = vendor(e)
    vis = [t for t in (e.get('tickets') or []) if visible(t)]
    row = (e['id'], d, v, len(vis), e.get('genre'), (e.get('artist') or '')[:30],
           (e.get('name') or '')[:40])
    if vis:
        alive.append(row)
    past.append(row)
    byvendor[v] += 1
    byday[d[:7]] += 1

out = io.open('tmp/del_classify_0921.txt', 'w', encoding='utf-8')
out.write('today=%s  公演が終わったエントリ %d件\n' % (TODAY, len(past)))
out.write('うち「まだ画面に枠が出る」子 %d件（配信・売り切れ印など）\n\n' % len(alive))
out.write('--- 売り場別 ---\n')
for k, n in byvendor.most_common():
    out.write('  %-8s %5d件\n' % (k, n))
out.write('\n--- 公演月別 ---\n')
for k, n in sorted(byday.items()):
    out.write('  %s %5d件\n' % (k, n))
out.write('\n--- ジャンル別 ---\n')
g = collections.Counter(r[4] for r in past)
for k, n in g.most_common():
    out.write('  %-10s %5d件\n' % (k, n))
out.write('\n=== 枠が出る子（消す前に中身を見る） ===\n')
for r in sorted(alive, key=lambda x: x[1]):
    out.write('id=%-6s %s %-8s 枠%d %-10s %s / %s\n' % r)
out.write('\n=== 公演終了・枠なし（削除候補）id一覧 ===\n')
ids = [str(r[0]) for r in past if r[0] not in {a[0] for a in alive}]
out.write(','.join(ids) + '\n')
out.write('\n件数=%d\n' % len(ids))
out.close()
print('wrote tmp/del_classify_0921.txt  past=%d alive=%d cand=%d'
      % (len(past), len(alive), len(ids)))
