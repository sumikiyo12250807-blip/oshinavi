# -*- coding: utf-8 -*-
"""投入用の候補を作り直す。
  ①バッチ内で同じツアーが2エントリに割れている7組を1つに畳む（URLを両方渡す＝multi=Trueで
    ticket.url が刻まれる。memory: feedback_build_pia_multiurl_loses_ticket_url）
  ②既存と統合すべきか判断がつかない14件は投入しない（保留して報告）
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [(6078, 6079), (6099, 6100), (6101, 6102), (6104, 6105),
         (6134, 6135), (6142, 6143), (6184, 6185)]
HOLD = {6070, 6087, 6088, 6094, 6103, 6110, 6113, 6144, 6161, 6163, 6173, 6175, 6179, 6180}

src = {c['newid']: c for c in json.load(open('tmp/_newbuild_in_0901.json', encoding='utf-8'))}
merge_into = {}
for a, b in PAIRS:
    merge_into[b] = a

out, nid = [], 6070
for k in sorted(src):
    if k in HOLD or k in merge_into:
        continue
    urls = list(src[k]['urls'])
    for b, a in merge_into.items():
        if a == k:
            urls += [u for u in src[b]['urls'] if u not in urls]
    out.append({'newid': nid, 'artist': src[k]['artist'], 'urls': urls})
    nid += 1

json.dump(out, open('tmp/_newbuild_in2_0901.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'投入候補 {len(out)}件（畳んだ組 {len(PAIRS)} / 保留 {len(HOLD)}）→ id {6070}-{nid - 1}')
