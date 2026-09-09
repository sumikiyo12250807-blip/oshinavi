# -*- coding: utf-8 -*-
"""統合行き（名前が既存と同じ）を、既存エントリのidに割り当てて候補ファイルを作る。

🚨部分一致で畳まない（「新日本フィル」が消える事故）＝正規化した**完全一致**だけ。
🚨1件につき1URL（複数URLを渡すと2本目以降に ticket.url が付かない
  ＝[[feedback_build_pia_multiurl_loses_ticket_url]]）。
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
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[『』「」【】（）\(\)＜＞<>\[\]［］～〜\-‐−–—・,、.。/／!！?？:：;；"\'”’]', '', s)
    return s.lower()


h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
idx = collections.defaultdict(list)
for e in events:
    idx[norm(e.get('name'))].append(e)

merge = json.load(io.open('tmp/merge_0910.json', encoding='utf-8'))
cands, ambiguous, nohit = [], [], []
for c in merge:
    hits = idx.get(norm(c['artist']), [])
    if not hits:
        nohit.append(c)
    elif len(hits) > 1:
        ambiguous.append((c, hits))
    else:
        cands.append({'newid': hits[0]['id'], 'artist': c['artist'], 'urls': [c['url']]})

print('統合行き %d件 → 相手が1件に決まる %d / 相手が複数 %d / 相手が見つからない %d'
      % (len(merge), len(cands), len(ambiguous), len(nohit)))
for c, hits in ambiguous:
    print('  ⚠️ %s → 候補 %s' % (c['artist'][:40], [e['id'] for e in hits]))
for c in nohit:
    print('  ⚠️ 相手なし %s' % c['artist'][:40])

json.dump(cands, io.open('tmp/cand_merge_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('→ tmp/cand_merge_0910.json')
