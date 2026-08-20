# -*- coding: utf-8 -*-
"""今朝のharvest在庫を「発売日までの残り日数」で分布を出す。
50件/日で足りているのか、2週間先の在庫はどれだけあるのかを事実で見る。"""
import json, io, sys, glob, re, datetime, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = datetime.date(2026, 7, 10)

def parse_rls(r):
    if not r or r == 'TODAY':
        return 0
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', r)
    if not m: return None
    d = datetime.date(*[int(x) for x in m.groups()])
    return (d - TODAY).days

buckets = collections.Counter()
per_tag = collections.defaultdict(collections.Counter)
total = 0
for f in sorted(glob.glob('tmp/presale_*_0710.json')):
    tag = re.search(r'presale_(.+?)_0710', f).group(1)
    d = json.load(open(f, encoding='utf-8'))
    for it in d.get('new', []):
        n = parse_rls(it.get('rlsdate', ''))
        total += 1
        if n is None: key = '?'
        elif n <= 0:  key = '本日発売'
        elif n == 1:  key = '明日発売'
        elif n <= 3:  key = '2〜3日後'
        elif n <= 7:  key = '4〜7日後'
        elif n <= 14: key = '8〜14日後'
        elif n <= 30: key = '15〜30日後'
        else:         key = '31日以上先'
        buckets[key] += 1
        per_tag[tag][key] += 1

ORDER = ['本日発売', '明日発売', '2〜3日後', '4〜7日後', '8〜14日後', '15〜30日後', '31日以上先', '?']
print(f'=== 今朝のharvest未掲載 在庫 合計 {total}件（発売日までの残り日数）===\n')
for k in ORDER:
    if buckets[k]:
        bar = '█' * min(60, buckets[k] // 8 + 1)
        print(f'  {k:<10} {buckets[k]:>5}件  {bar}')
print(f'\n  ★ 4日後以降（カウントダウンの価値あり）= {sum(buckets[k] for k in ["4〜7日後","8〜14日後","15〜30日後","31日以上先"])}件')
print(f'  ▲ 今日・明日 = {buckets["本日発売"] + buckets["明日発売"]}件\n')
print('--- ジャンル別 ---')
for tag in per_tag:
    row = ' / '.join(f'{k}:{per_tag[tag][k]}' for k in ORDER if per_tag[tag][k])
    print(f'  {tag:<12} 計{sum(per_tag[tag].values()):>4}  {row}')
