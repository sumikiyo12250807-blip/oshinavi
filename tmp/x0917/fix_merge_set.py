# -*- coding: utf-8 -*-
"""畳む対象を人の判断で直す（2026-09-16 夜・X準備の総ざらい第2弾）。

split_built_0916.py は名前の完全一致で畳み先を決めるので、次の2つを手で直す。
 ①名曲コンサート5件（11072〜11075・11077）を**畳まない**
   ＝id7907 は「一般発売（神奈川 R9年 2/13公演）」1枠だけのエントリ。
     候補はキスポート／セントラル愛知／土師さおり／東京フィル／劉福君二胡＝別主催の別公演で、
     一般名詞で名前が一致しただけ。畳んだら1エントリに無関係な公演を混ぜることになる。
 ②佐野元春&THE COYOTE BAND 2件（11052 静岡11/14・11066 佐賀9/26〜9/27）を id3117 へ
   ＝完全一致が3件出て機械が決められなかった。7113（福岡の先行1枠）・7114（熊本の先行1枠）は
     単発の先行エントリで、3117 がツアー本体（11枠）。ツアーは1エントリに集める。

出力: tmp/x0917/merge_built2.json ／ tmp/x0917/merge_cands2.json
使い方: python tmp/x0917/fix_merge_set.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DROP = {11072, 11073, 11074, 11075, 11077}   # 名曲コンサート＝畳まない
ADD = {11052: 3117, 11066: 3117}             # 佐野元春＝ツアー本体へ

built = {b['id']: b for b in json.load(io.open('tmp/x0917/built2.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/x0917/cands2.json', encoding='utf-8'))}
mb = json.load(io.open('tmp/merge_built_x0917b.json', encoding='utf-8'))
mc = {c['newid']: c for c in json.load(io.open('tmp/merge_cands_x0917b.json', encoding='utf-8'))}

out_b, out_c = [], []
for b in mb:
    if b['id'] in DROP:
        continue
    out_b.append(b)
    out_c.append(mc[b['id']])
for nid, target in ADD.items():
    c = dict(cands[nid])
    c['target'] = target
    out_b.append(built[nid])
    out_c.append(c)

assert len(out_b) == len(out_c) == 14, (len(out_b), len(out_c))
assert all(c.get('target') for c in out_c)
json.dump(out_b, io.open('tmp/x0917/merge_built2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(out_c, io.open('tmp/x0917/merge_cands2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('fold=%d' % len(out_b))
for c in out_c:
    print('  new%-6d -> id%-6d slots=%d' % (
        c['newid'], c['target'], len(built[c['newid']].get('tickets') or [])))
print('drop(nokyoku)=%s' % sorted(DROP))
