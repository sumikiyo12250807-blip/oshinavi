# -*- coding: utf-8 -*-
"""音楽の受付中の未登録候補を「今夜組む新規」と「朝に回す既存名」に分ける（読むだけ・2026-09-15 夜）
・名前（正規化）がまだ登録に無いもの＝新規。同じ名前の売り場は1つの候補にまとめる（ツアーは1エントリ＝feedback_tour_consolidate）
  → tmp/cands_uk01new_0915.json（build_pia_entries にそのまま渡せる形・newid は 10763 から振り直し）
・同じ名前のエントリが登録済みのもの＝既存へ枠を足す判断が要る（別人・別公演のこともある）→ 今夜は組まない
  → tmp/cands_uk01exist_0915.txt（朝にユーザーへ見せる一覧）
使い方: python cands_split_0915.py
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
g = collections.OrderedDict()
for c in cands:
    g.setdefault(norm(c['artist']), []).append(c)

start = min(c['newid'] for c in cands)
new, exist_lines, nid = [], [], start - 1
for k, v in g.items():
    if k in by_name:
        ids = sorted(set(by_name[k]))
        for c in v:
            exist_lines.append('%s｜既存id %s｜公演 %s %s｜%s' % (c['artist'], ids[:6], c.get('_perfdate'), c.get('_pref'), c['urls'][0]))
        continue
    nid += 1
    urls = []
    for c in v:
        for u in c['urls']:
            if u not in urls:
                urls.append(u)
    new.append({'newid': nid, 'artist': v[0]['artist'], 'urls': urls, '_lg': v[0].get('_lg'),
                '_perfdate': ' / '.join(c.get('_perfdate') or '' for c in v), '_pref': ' / '.join(c.get('_pref') or '' for c in v)})
json.dump(new, io.open('tmp/cands_uk01new_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/cands_uk01exist_0915.txt', 'w', encoding='utf-8').write('\n'.join(exist_lines) + '\n')
print('今夜組む新規 %d件（売り場 %d本・id %d〜%d）→ tmp/cands_uk01new_0915.json' % (len(new), sum(len(c['urls']) for c in new), new[0]['newid'], new[-1]['newid']))
print('朝に回す既存名 %d行 → tmp/cands_uk01exist_0915.txt' % len(exist_lines))
