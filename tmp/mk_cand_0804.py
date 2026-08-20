# -*- coding: utf-8 -*-
"""発売前スイープの残り → build_pia_entries 用の候補JSONを作る（8/4分）。
・1バッチ50エントリ上限（feedback_new50_silent_selfrun）
・同一artistは1エントリにurlsをまとめる（feedback_tour_consolidate）
・既存登録のeventCd/BundleCdは二重登録しない（feedback_harvest_dedup_check）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

LIMIT = 50
rows = json.load(io.open('tmp/ps_merge_0803.json', encoding='utf-8'))

h = io.open('index.html', encoding='utf-8', newline='').read()
evs = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
maxid = max(e['id'] for e in evs)
exist_cd = set()
for e in evs:
    blob = json.dumps(e, ensure_ascii=False)
    exist_cd |= set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', blob))
# 既存の正規化アーティスト名（同名の別エントリを作らないための目視用）
exist_names = {re.sub(r'\s+', '', (e.get('artist') or '')) for e in evs}


def norm(u):
    m = re.search(r'eventBundleCd=([0-9a-zA-Z]+)', u)
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + m.group(1), m.group(1)
    m = re.search(r'eventCd=(\d+)', u)
    return ('https://t.pia.jp/pia/event/event.do?eventCd=' + m.group(1), m.group(1)) if m else (None, None)


groups, order, skipped, dupname = {}, [], [], []
for r in rows:
    u, cd = norm(r['url'])
    if not u:
        continue
    if cd in exist_cd:
        skipped.append((r['artist'], cd))
        continue
    a = r['artist']
    if a not in groups:
        if len(groups) >= LIMIT:
            continue
        if re.sub(r'\s+', '', a) in exist_names:
            dupname.append(a)
        groups[a] = []
        order.append(a)
    if u not in groups[a]:
        groups[a].append(u)

cands = [{'newid': maxid + 1 + i, 'artist': a, 'urls': groups[a]} for i, a in enumerate(order)]
json.dump(cands, io.open('tmp/cand_0804.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
lines = ['候補 %d エントリ / URL計 %d本 / 既存重複でskip %d件 / newid %d..%d'
         % (len(cands), sum(len(c['urls']) for c in cands), len(skipped),
            cands[0]['newid'], cands[-1]['newid'])]
if dupname:
    lines.append('⚠️同名アーティストが既存にある(要目視) %d件: %s' % (len(dupname), ' / '.join(dupname)))
for c in cands:
    lines.append('  %d %s (%d本)' % (c['newid'], c['artist'], len(c['urls'])))
io.open('tmp/cand_0804.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote tmp/cand_0804.json / tmp/cand_0804.txt  cands=%d skipped=%d dupname=%d'
      % (len(cands), len(skipped), len(dupname)))
