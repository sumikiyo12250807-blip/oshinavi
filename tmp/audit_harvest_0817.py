# -*- coding: utf-8 -*-
"""8/17朝の新着収集が「何をどれだけ拾って、何件が発売前だったか」を機械で数え直す。"""
import io, os, re, sys, json, glob, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

print('=== ぴあ発売前スイープの生の在庫（tmp/presale_*_0817.json） ===')
for f in sorted(glob.glob('tmp/presale_*_0817.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    keys = {k: (len(v) if isinstance(v, list) else v) for k, v in d.items()}
    print('  %-34s %s' % (os.path.basename(f), keys))

print()
print('=== 受付中スイープの生の在庫（tmp/open_*_0817.json） ===')
for f in sorted(glob.glob('tmp/open_*_0817.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    keys = {k: (len(v) if isinstance(v, list) else v) for k, v in d.items()}
    print('  %-34s %s' % (os.path.basename(f), keys))

print()
print('=== 実際に投入された 4426-4488 の中身 ===')
idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
today = datetime.date(2026, 8, 17)


def d(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


pre, onsale, other = [], [], []
for e in EV:
    if not (4426 <= e['id'] <= 4488):
        continue
    ts = e.get('tickets') or []
    # 発売前＝startDate が今日より後の枠が1つでもある
    starts = [d(t.get('startDate')) for t in ts if t.get('startDate')]
    ends = [d(t.get('date')) for t in ts if t.get('date')]
    fut = [s for s in starts if s and s > today]
    row = (e['id'], e.get('artist', '')[:28],
           min([s for s in starts if s]).isoformat() if [s for s in starts if s] else '-',
           max([x for x in ends if x]).isoformat() if [x for x in ends if x] else '-')
    if fut:
        pre.append(row)
    elif ends and max([x for x in ends if x]) >= today:
        onsale.append(row)
    else:
        other.append(row)

print('  発売前(これから売る枠あり) %d件 / もう売ってる %d件 / その他 %d件  = 計%d件'
      % (len(pre), len(onsale), len(other), len(pre) + len(onsale) + len(other)))
print()
print('  --- 発売前 ---')
for r in pre:
    print('   %5d %-28s 発売開始 %s  締切 %s' % r)
print('  --- もう売ってる（穴埋め分） ---')
for r in onsale:
    print('   %5d %-28s 発売開始 %s  締切 %s' % r)
if other:
    print('  --- その他 ---')
    for r in other:
        print('   %5d %-28s 発売開始 %s  締切 %s' % r)
