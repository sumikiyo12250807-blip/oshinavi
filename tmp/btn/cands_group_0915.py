# -*- coding: utf-8 -*-
"""音楽の受付中の未登録候補（tmp/cands_uk01night_0915.json）を名前でまとめて数える（読むだけ・2026-09-15 夜）
・同じ名前（正規化）が何件あるか＝ツアーを1エントリにまとめる対象
・同じ名前のエントリがもう登録されているか＝新しく作らず既存へ枠を足す対象
使い方: python cands_group_0915.py → 画面に集計・tmp/btn_tpl/cands_group.txt に明細
"""
import collections
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\']', '', s)


cands = json.load(io.open('tmp/cands_uk01night_0915.json', encoding='utf-8'))
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by_name = collections.defaultdict(list)
for e in ev:
    for k in {norm(e.get('artist')), norm(e.get('name'))}:
        if k:
            by_name[k].append(e['id'])
g = collections.defaultdict(list)
for c in cands:
    g[norm(c['artist'])].append(c)
multi = {k: v for k, v in g.items() if len(v) > 1}
exist = {k: v for k, v in g.items() if k in by_name}
with io.open('tmp/btn_tpl/cands_group.txt', 'w', encoding='utf-8') as f:
    for k, v in sorted(g.items(), key=lambda x: -len(x[1])):
        f.write('%s｜%d件｜既存=%s｜%s\n' % (v[0]['artist'][:30], len(v), by_name.get(k, [])[:5], ' / '.join((c.get('_perfdate') or '') + ' ' + (c.get('_pref') or '') for c in v)))
print('候補 %d件 → 名前 %d種類' % (len(cands), len(g)))
print('同じ名前が2件以上 %d種類（候補 %d件）' % (len(multi), sum(len(v) for v in multi.values())))
print('同じ名前のエントリが登録済み %d種類（候補 %d件）' % (len(exist), sum(len(v) for v in exist.values())))
print('どちらでもない＝1件だけで新規 %d件' % sum(1 for k, v in g.items() if len(v) == 1 and k not in by_name))
