import json, sys
sys.stdout.reconfigure(encoding='utf-8')
cands = json.load(open('tmp/cand_pia_0725b.json', encoding='utf-8'))
take = cands[20:22]
for i, c in enumerate(take):
    c['newid'] = 3268 + i
json.dump(take, open('tmp/cand_pia_topup.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('追加2件 id3268,3269')
