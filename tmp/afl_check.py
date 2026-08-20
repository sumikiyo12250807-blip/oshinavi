# -*- coding: utf-8 -*-
"""新着の楽天リンクが全部アフィリ(Deep Link)形式かを機械で確認する。"""
import json, re, sys, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

DEEP = 'https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl='
news = [e for e in EV if e.get('genre') == 'new']
rk = [e for e in news if (e.get('links') or {}).get('rakuten')]
print('新着 %d件 / うち楽天リンクあり %d件\n' % (len(news), len(rk)))

ng = []
url_cnt = 0
for e in rk:
    urls = [('links.rakuten', e['links']['rakuten'])]
    for t in e.get('tickets', []):
        if t.get('url'):
            urls.append(('ticket', t['url']))
    for where, u in urls:
        url_cnt += 1
        if not u.startswith(DEEP):
            ng.append((e['id'], where, u[:70]))
            continue
        murl = urllib.parse.unquote(u[len(DEEP):])
        if not murl.startswith('https://ticket.rakuten.co.jp/'):
            ng.append((e['id'], where + '(murl不正)', murl[:70]))

print('チェックしたURL数:', url_cnt)
if ng:
    print('🚨 アフィリでないURL %d件' % len(ng))
    for i, w, u in ng:
        print('   id=%s %s %s' % (i, w, u))
else:
    print('✅ 全部 Deep Link 形式（id=z9x6HLNpWco / mid=53531）・murlは楽天の個別公演ページ')

# 既存側の楽天リンクも一応
old = [e for e in EV if e.get('genre') != 'new' and (e.get('links') or {}).get('rakuten')]
bare = [e for e in old if e['links']['rakuten'].startswith('https://ticket.rakuten.co.jp/')]
print('\n既存で楽天リンクあり %d件 / うち素URL(アフィリ無し) %d件' % (len(old), len(bare)))
for e in bare[:10]:
    print('   id=%s %s' % (e['id'], (e.get('name') or '')[:40]))
