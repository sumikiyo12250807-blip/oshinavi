# -*- coding: utf-8 -*-
"""「楽天でも買えるのにリンクが無い」18件を (既存id, 楽天URL) の組にする。"""
import collections
import io
import json
import re
import sys
import unicodedata
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[『』「」【】（）\(\)＜＞<>\[\]［］～〜\-‐−–—・,、.。/／!！?？:：;；"\'”’]', '', s)
    return s.lower()


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def nurl(u):
    return re.sub(r'/+$', '', (u or '').split('?')[0]).lower()


d = json.load(io.open('tmp/rakuten_presale_0910.json', encoding='utf-8'))
live = d['presale'] + d['onsale']

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

have, byname = set(), collections.defaultdict(list)
for e in events:
    byname[norm(e.get('name'))].append(e)
    for u in [raw_url((e.get('links') or {}).get('rakuten'))] + \
             [raw_url(t.get('url')) for t in (e.get('tickets') or [])]:
        if 'rakuten' in (u or ''):
            have.add(nurl(u))

pairs = []
for x in live:
    if nurl(x['url']) in have:
        continue
    hits = byname.get(norm(RH.norm_name(x['name']))) or byname.get(norm(x['name']))
    if not hits:
        continue
    if len(hits) > 1:
        print('⚠️ 相手が複数なので外す: %s → %s' % (x['name'][:40], [e['id'] for e in hits]))
        continue
    pairs.append({'id': hits[0]['id'], 'url': x['url'], 'name': x['name']})

json.dump(pairs, io.open('tmp/rakuten_link_pairs_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('組にできた %d件 → tmp/rakuten_link_pairs_0910.json' % len(pairs))
