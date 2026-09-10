# -*- coding: utf-8 -*-
"""「楽天でも売っているのに楽天リンクを貼れていないエントリ」を数える。

ユーザーの提案（2026-09-10）＝
  「ぴあのリンクは0円だけど楽天チケットはアフィリあるから、楽天チケットのリンクで貼って
   情報はぴあから収集して、そのほうが確実じゃない？」

🚫ただし決まりに釘が刺してある（[[feedback_vendor_priority]]）＝
  「そこで売っていないのに楽天リンクを貼らない。優先順位は**探す順番**であって
   **無理やり埋める順番**ではない」。だから先に「楽天にも在るのか」を数える。

材料＝今日のハーベスト結果（tmp/rakuten_presale_0910.json）の
  presale（これから発売）＋ onsale（販売中）＝**いま楽天で買えるページ**。
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

have_url = set()
byname = collections.defaultdict(list)
for e in events:
    byname[norm(e.get('name'))].append(e)
    for u in [raw_url((e.get('links') or {}).get('rakuten'))] + \
             [raw_url(t.get('url')) for t in (e.get('tickets') or [])]:
        if 'rakuten' in (u or ''):
            have_url.add(nurl(u))

linked, matched, nomatch = [], [], []
for x in live:
    if nurl(x['url']) in have_url:
        linked.append(x)
        continue
    hits = byname.get(norm(RH.norm_name(x['name']))) or byname.get(norm(x['name']))
    if hits:
        matched.append((x, hits))
    else:
        nomatch.append(x)

print('いま楽天で買えるページ %d件（これから発売 %d ＋ 販売中 %d）'
      % (len(live), len(d['presale']), len(d['onsale'])))
print('  ① もう楽天リンクを貼ってある        %d件' % len(linked))
print('  ② 🎯**同じ名前の登録があるのに貼れていない** %d件' % len(matched))
print('  ③ 登録そのものが無い（新規候補）      %d件' % len(nomatch))

with io.open('tmp/rakuten_overlap_0910.md', 'w', encoding='utf-8') as f:
    f.write('# 楽天でも買えるのにリンクを貼れていないエントリ（%s）\n\n' % '2026-09-10')
    f.write('楽天で買えるページ %d件 ＝ 貼ってある %d / **貼れていない %d** / 登録なし %d\n\n'
            % (len(live), len(linked), len(matched), len(nomatch)))
    f.write('## 🎯 同じ名前の登録があるのに楽天リンクが無い\n\n')
    for x, hits in matched:
        f.write('- %s\n' % x['name'][:60])
        for e in hits[:3]:
            ls = e.get('links') or {}
            f.write('    ⇔ 既存 id=%s [%s] 公演%s ／ ぴあ=%s\n'
                    % (e['id'], e.get('genre'), e.get('date'), 'あり' if ls.get('pia') else 'なし'))
        f.write('  - %s\n' % x['url'])
    f.write('\n## 登録そのものが無い（新規候補）\n\n')
    for x in nomatch:
        f.write('- %s ／ 公演 %s〜%s ／ %s\n' % (x['name'][:60], x['first'], x['last'], x['url']))
print('\n→ tmp/rakuten_overlap_0910.md')
