# -*- coding: utf-8 -*-
"""統合行き（tmp/merge_0912.json＝未登録ページだが、同じ名前の既存エントリがある）の足す先を決める（読むだけ）。
・既存で正規化名が一致するエントリが**1つだけ** → 足す先に決める
・2つ以上 → 保留（どれに足すか人が決める）／0 → 新規扱いに回す（名前の揺れ）
🚨ぴあ由来のアーティストが同じでも「別の興行」はある（ディナーショーとツアー等）。
   ここでは候補を出すだけ。足す前にビルドして、会場・公演日が既存ツアーの続きかを見る。
使い方: python tmp/merge_map_0912.py
出力: tmp/merge_map_0912.json（[{eventCd,url,artist,target,cands}]）
"""
import collections
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by_name = collections.defaultdict(list)
for e in ev:
    for f in ('artist', 'name'):
        k = norm(e.get(f))
        if k and e['id'] not in by_name[k]:
            by_name[k].append(e['id'])

rows = json.load(io.open('tmp/merge_0912.json', encoding='utf-8'))
out, one, many, none = [], 0, 0, 0
for r in rows:
    c = by_name.get(norm(r['artist']), [])
    t = c[0] if len(c) == 1 else None
    if len(c) == 1:
        one += 1
    elif len(c) > 1:
        many += 1
    else:
        none += 1
    out.append({'eventCd': r['eventCd'], 'url': r['url'], 'artist': r['artist'], 'lg': r.get('lg'),
                'rlsdate': r.get('rlsdate'), 'target': t, 'cands': c[:8]})
json.dump(out, io.open('tmp/merge_map_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('統合行き %d件 ＝ 足す先が1つ %d ／ 2つ以上（保留） %d ／ 見つからない %d' % (len(rows), one, many, none))
for o in out:
    if o['target'] is None:
        print('  保留 %s | %s | 候補=%s' % (o['eventCd'], o['artist'][:30], o['cands']))
