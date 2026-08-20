# -*- coding: utf-8 -*-
"""3ジャンルの候補からeventCd重複を弾いて50件選定。candidates.json出力。"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
idx = open('index.html', encoding='utf-8').read()
# 既存の全eventCd/BundleCd
exist_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))

def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else None

def load(f):
    return json.load(open(f, encoding='utf-8'))['new']

quota = [('tmp/ps_engeki.json', 20), ('tmp/ps_music.json', 18), ('tmp/ps_classic.json', 12)]
picked = []
used_cds = set()
nid = 1087
for f, q in quota:
    cnt = 0
    for it in load(f):
        if cnt >= q: break
        cd = cd_of(it['url'])
        if not cd or cd in exist_cds or cd in used_cds:
            continue
        used_cds.add(cd)
        picked.append({'newid': nid, 'artist': it['artist'], 'urls': [it['url']],
                       '_src': f.split('_')[-1].replace('.json',''), '_perf': it.get('perfdate',''), '_rls': it.get('rlsdate','')})
        nid += 1; cnt += 1
    print(f"{f}: 選定{cnt}件")
json.dump(picked, open('tmp/candidates50.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n合計', len(picked), '件  id', picked[0]['newid'], '..', picked[-1]['newid'])
for p in picked:
    print(f"  {p['newid']} [{p['_src']}] {p['artist'][:30]} | 発売{p['_rls']} | 公演{p['_perf'][:18]}")
