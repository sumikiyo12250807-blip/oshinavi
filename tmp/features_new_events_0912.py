# -*- coding: utf-8 -*-
"""特設ページから辿れた公演ページのうち、**まだ見ていないもの**を洗い出す（読むだけ・9/10版を今日の形に合わせた）。

・すでに登録に楽天URLとして入っている → 既知
・今朝の post-sitemap スイープ（tmp/rakuten_presale.json）で見た → 既知
・どちらでもない → **特設ページからしか辿れない公演**
🚨今日の tmp/rakuten_features.json は公演URLがページごと（pages[].events）に入る形。最上段の events があればそれも足す。
"""
import io
import json
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')


def raw_url(u):
    u = u or ''
    m = re.search(r'murl=([^&]+)', u) or re.search(r'pc=([^&]+)', u)
    return urllib.parse.unquote(urllib.parse.unquote(m.group(1))) if m else u


def nurl(u):
    return re.sub(r'/+$', '', (u or '').split('?')[0]).lower()


feat = json.load(io.open('tmp/rakuten_features.json', encoding='utf-8'))
events_from_features = {nurl(u) for u in feat.get('events') or []}
for p in feat.get('pages') or []:
    events_from_features |= {nurl(u) for u in p.get('events') or []}

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
registered = set()
for e in json.loads(m.group(2)):
    for u in [raw_url((e.get('links') or {}).get('rakuten'))] + \
             [raw_url(t.get('url')) for t in (e.get('tickets') or [])]:
        if 'rakuten' in (u or ''):
            registered.add(nurl(u))

seen = set()
d = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8-sig'))
for k in ('presale', 'onsale', 'soldout', 'past', 'error'):
    for x in d.get(k) or []:
        seen.add(nurl(x['url']))

only_feat = sorted(events_from_features - registered - seen)
print('特設ページから辿れた公演ページ %d本' % len(events_from_features))
print('  うち登録済み            %d本' % len(events_from_features & registered))
print('  うち今朝のスイープで見た  %d本' % len(events_from_features & seen))
print('  🎯どちらでもない        %d本' % len(only_feat))
io.open('tmp/features_only_urls_0912.json', 'w', encoding='utf-8').write(
    json.dumps(only_feat, ensure_ascii=False, indent=1))
print('→ tmp/features_only_urls_0912.json')
