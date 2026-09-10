# -*- coding: utf-8 -*-
"""特設ページから辿れた公演ページ223本のうち、**まだ見ていないもの**を洗い出す。

・すでに登録に楽天URLとして入っている → 既知
・今日の post-sitemap スイープ（1,262本）で見た → 既知
・どちらでもない → **特設ページからしか辿れなかった公演**＝入口の穴の実害
"""
import io
import json
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def nurl(u):
    return re.sub(r'/+$', '', (u or '').split('?')[0]).lower()


feat = json.load(io.open('tmp/rakuten_features_0910.json', encoding='utf-8'))
events_from_features = {nurl(u) for u in feat['events']}

# ① 登録にある楽天URL
h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
registered = set()
for e in json.loads(m.group(2)):
    for u in [raw_url((e.get('links') or {}).get('rakuten'))] + \
             [raw_url(t.get('url')) for t in (e.get('tickets') or [])]:
        if 'rakuten' in (u or ''):
            registered.add(nurl(u))

# ② 今日の post-sitemap スイープで見たURL
seen = set()
d = json.load(io.open('tmp/rakuten_presale_0910.json', encoding='utf-8'))
for k in ('presale', 'onsale', 'soldout', 'past'):
    for x in d.get(k) or []:
        seen.add(nurl(x['url']))
for x in d.get('error') or []:
    seen.add(nurl(x['url']))

only_feat = sorted(events_from_features - registered - seen)
print('特設ページから辿れた公演ページ %d本' % len(events_from_features))
print('  うち登録済み            %d本' % len(events_from_features & registered))
print('  うち今日のスイープで見た  %d本' % len(events_from_features & seen))
print('  🎯**どちらでもない**      %d本' % len(only_feat))

io.open('tmp/features_only_urls_0910.json', 'w', encoding='utf-8').write(
    json.dumps(only_feat, ensure_ascii=False, indent=1))
for u in only_feat[:40]:
    print('   %s' % u)
print('\n→ tmp/features_only_urls_0910.json')
