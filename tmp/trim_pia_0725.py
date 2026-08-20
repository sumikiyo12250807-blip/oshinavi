import json, sys
sys.stdout.reconfigure(encoding='utf-8')

cands = json.load(open('tmp/cand_pia_0725b.json', encoding='utf-8'))
take = cands[:20]
for i, c in enumerate(take):
    c['newid'] = 3248 + i
json.dump(take, open('tmp/cand_pia_trim.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ぴあ候補 %d件 → 先頭20件を id3248..%d に採番' % (len(cands), 3248 + len(take) - 1))
for c in take:
    print('  %s %s' % (c['newid'], (c.get('title') or c.get('name') or '')[:46]))
