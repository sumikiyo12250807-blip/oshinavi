# -*- coding: utf-8 -*-
"""楽天の発売前ハーベストの結果を「既存に足す」と「新規で入れる」に分ける。

  python tmp/rakuten_presale_split_0910.py [tmp/rakuten_presale_0910.json]

・既存＝そのページURLを既に持っているエントリがある（＝**枠を足す側**。
  理芽・KOKO・春猿火のように、登録済みなのに発売前の枠だけ抜けている型）
・新規＝どのエントリも持っていないURL（＝ビルドして新着プールへ）
🚨名前だけで名寄せしない（[[feedback_harvest_name_dedup_blindspot]]）。URLで突き合わせ、
  そのうえで正規化名でも当てて「同名だがURLが違う」を別に出す。
"""
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

SRC = sys.argv[1] if len(sys.argv) > 1 else 'tmp/rakuten_presale_0910.json'


def raw_url(u):
    m = re.search(r'murl=([^&]+)', u or '')
    return urllib.parse.unquote(m.group(1)) if m else (u or '')


def norm_url(u):
    return re.sub(r'/+$', '', (u or '').split('?')[0]).lower()


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[『』「」【】（）\(\)＜＞<>\[\]［］～〜\-‐−–—・,、.。/／!！?？:：;；"\'”’]', '', s)
    return s.lower()


d = json.load(io.open(SRC, encoding='utf-8'))
pre = d['presale']

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

url2e, name2e = {}, collections.defaultdict(list)
for e in events:
    name2e[norm(e.get('name'))].append(e)
    us = [raw_url((e.get('links') or {}).get('rakuten'))]
    us += [raw_url(t.get('url')) for t in (e.get('tickets') or [])]
    for u in us:
        if 'rakuten' in (u or ''):
            url2e[norm_url(u)] = e

addto, samename, fresh = [], [], []
for x in pre:
    e = url2e.get(norm_url(x['url']))
    if e:
        addto.append((x, e))
        continue
    hits = name2e.get(norm(RH.norm_name(x['name'])) or norm(x['name']), [])
    if hits:
        samename.append((x, hits))
    else:
        fresh.append(x)

print('発売前のページ %d件' % len(pre))
print('  ① 既存が同じURLを持っている（枠を足す）      %d件' % len(addto))
print('  ② 名前は同じだがURLが違う（1件ずつ見る）     %d件' % len(samename))
print('  ③ まったくの新規（ビルドして投入）           %d件' % len(fresh))

with io.open('tmp/rakuten_presale_split_0910.md', 'w', encoding='utf-8') as f:
    f.write('# 楽天「これから発売」の仕分け（%s）\n\n' % SRC)
    f.write('発売前のページ **%d件** ＝ 既存に足す %d / 同名だがURL違い %d / 新規 %d\n'
            % (len(pre), len(addto), len(samename), len(fresh)))

    f.write('\n## ① 既存に発売前の枠を足す\n\n')
    for x, e in addto:
        f.write('- id=%s %s\n' % (e['id'], x['name'][:56]))
        for w in x['presale_windows']:
            f.write('  - 🎯%s | %s\n' % (w['type'], w['timming']))
        f.write('  - %s\n' % x['url'])

    f.write('\n## ② 名前は同じだがURLが違う（別公演か別ページか見る）\n\n')
    for x, hits in samename:
        f.write('- %s\n' % x['name'][:56])
        for e in hits[:3]:
            f.write('    ⇔ 既存 id=%s [%s] 公演%s\n' % (e['id'], e.get('genre'), e.get('date')))
        f.write('  - %s\n' % x['url'])

    f.write('\n## ③ 新規（ビルドして投入）\n\n')
    for x in fresh:
        f.write('- %s ／ 公演 %s〜%s ／ _genre=%s\n' % (x['name'][:56], x['first'], x['last'], x['_genre']))
        for w in x['presale_windows']:
            f.write('  - 🎯%s | %s\n' % (w['type'], w['timming']))
        f.write('  - %s\n' % x['url'])

json.dump([x['url'] for x in fresh], io.open('tmp/rakuten_presale_fresh_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump([{'id': e['id'], 'url': x['url'], 'name': x['name'],
            'presale_windows': x['presale_windows']} for x, e in addto],
          io.open('tmp/rakuten_presale_addto_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('→ tmp/rakuten_presale_split_0910.md ／ *_fresh_0910.json ／ *_addto_0910.json')
