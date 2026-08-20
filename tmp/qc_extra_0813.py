# -*- coding: utf-8 -*-
"""新着プール追加QC：売り場リンク欠落／日付のcap逆転／発売日>終了日／要相談リスト"""
import json, re, sys, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = [e for e in EVENTS if e.get('genre') == 'new']


def d(s):
    try:
        return datetime.date(*[int(x) for x in s.split('-')])
    except Exception:
        return None


print('--- 売り場リンク欠落 ---')
n = 0
for e in news:
    lk = {k: v for k, v in (e.get('links') or {}).items() if v}
    if not any(k in lk for k in ('pia', 'eplus', 'lawson', 'rakuten')):
        n += 1
        print('  🚨 id=%d %s links=%s' % (e['id'], e['name'][:30], list(lk)))
print('  欠落 %d件' % n)

print('\n--- 販売終了日 > 公演日（cap逆転） ---')
n = 0
for e in news:
    ev = d(e.get('date') or '')
    for t in e.get('tickets') or []:
        td = d(t.get('date') or '')
        if ev and td and td > ev:
            n += 1
            print('  🚨 id=%d %s | 締切%s > 公演%s' % (e['id'], e['name'][:26], t['date'], e['date']))
print('  逆転 %d枠' % n)

print('\n--- 発売開始日 > 販売終了日 ---')
n = 0
for e in news:
    for t in e.get('tickets') or []:
        sd, td = d(t.get('startDate') or ''), d(t.get('date') or '')
        if sd and td and sd > td:
            n += 1
            print('  🚨 id=%d %s | 発売%s > 締切%s' % (e['id'], e['name'][:26], t['startDate'], t['date']))
print('  逆転 %d枠' % n)

print('\n--- 発売開始日の分布（カウントダウン価値） ---')
today = datetime.date.today()
c = collections.Counter()
for e in news:
    ds = [d(t.get('startDate') or '') for t in e.get('tickets') or []]
    ds = [x for x in ds if x]
    if ds:
        c[(min(ds) - today).days] += 1
for k in sorted(c):
    print('  発売まで%2d日: %d件' % (k, c[k]))

print('\n--- 要相談（_piaSub 空/その他・未マップ） ---')
for e in news:
    sub = e.get('_piaSub') or ''
    if not sub or 'その他' in sub or e['id'] in (4224, 4225):
        print('  id=%d [%s] _genre=%s | %s' % (e['id'], sub or '空', e.get('_genre'), e['name'][:40]))

print('\n--- 全50件（id / _genre / 名前 / 公演日） ---')
for e in news:
    print('  %d\t%s\t%s\t%s' % (e['id'], e.get('_genre'), e['name'][:44], e.get('date')))
