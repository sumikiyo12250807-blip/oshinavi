# -*- coding: utf-8 -*-
"""発売前スイープの上位候補 → build_pia_entries 用の候補JSONを作る。
・1バッチ50エントリ上限（feedback_new50_silent_selfrun）
・同一artistは1エントリにurlsをまとめる（feedback_tour_consolidate）
・URLは t.pia.jp の正規形に直す（ticket.pia.jp は301の別名）
"""
import json, re, io, sys
sys.stdout.reconfigure(encoding='utf-8')

LIMIT = 50
rows = json.load(io.open('tmp/ps_merge_0803.json', encoding='utf-8'))

h = io.open('index.html', encoding='utf-8', newline='').read()
evs = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
maxid = max(e['id'] for e in evs)
# 既存に登録済みのeventCd/BundleCdは二重登録しない（feedback_harvest_dedup_check）
exist_cd = set()
for e in evs:
    blob = json.dumps(e, ensure_ascii=False)
    exist_cd |= set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', blob))


def norm(u):
    m = re.search(r'eventBundleCd=([0-9a-zA-Z]+)', u)
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + m.group(1), m.group(1)
    m = re.search(r'eventCd=(\d+)', u)
    return ('https://t.pia.jp/pia/event/event.do?eventCd=' + m.group(1), m.group(1)) if m else (None, None)


groups, order, skipped = {}, [], []
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
        groups[a] = []
        order.append(a)
    if u not in groups[a]:
        groups[a].append(u)

cands = [{'newid': maxid + 1 + i, 'artist': a, 'urls': groups[a]} for i, a in enumerate(order)]
json.dump(cands, io.open('tmp/cand_0803.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('候補 %d エントリ / URL計 %d本 / 既存重複でskip %d件 / newid %d..%d'
      % (len(cands), sum(len(c['urls']) for c in cands), len(skipped),
         cands[0]['newid'], cands[-1]['newid']))
for c in cands:
    print('  %d %s (%d本)' % (c['newid'], c['artist'], len(c['urls'])))
