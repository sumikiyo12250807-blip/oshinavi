# -*- coding: utf-8 -*-
"""Augusta Camp 2026 の締切がどこから来たかを実ページの生の値で示す。"""
import sys, re, json
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
e = next(x for x in json.loads(m.group(2)) if x['id'] == 3218)
print('=== 登録した中身 ===')
print(json.dumps({k: e[k] for k in ('id', 'name', 'date', 'dateLabel', 'venue', 'tickets')}, ensure_ascii=False, indent=1))

url = 'https://ticket.rakuten.co.jp/music/jpop/rthfkay/'
import urllib.parse
url = urllib.parse.unquote(e['links']['rakuten'].split('murl=')[1])
print('\n=== 実ページ %s ===' % url)
body = R.fetch(url)

print('\n--- 公演カードの生 data-date（ここから締切を取った）---')
for mm in list(re.finditer(r"<div class='performance([^']*)' data-date='(\{[^']*\})'>", body))[:4]:
    print('  class=%r' % mm.group(1), mm.group(2))

print('\n--- salesDisplayStatus（販売枠のJSON）---')
mm = re.search(r'var salesDisplayStatus = (.*?);', body, re.S)
print(' ', (mm.group(1)[:400] if mm else '無し'))

print('\n--- 本文の「販売期間」表記 ---')
txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))
for mm in list(re.finditer(r'販売期間.{0,90}', txt))[:3]:
    print(' ', mm.group(0))

print('\n--- パーサが読んだ値 ---')
for p in R.parse_perfs(body):
    print('  公演日=%s 会場=%s エリア=%s / 販売 %s 〜 %s / %s' % (
        p['date'], p['venue'], p['pref'], p['sale_start'], p['sale_end'], p['status']))
