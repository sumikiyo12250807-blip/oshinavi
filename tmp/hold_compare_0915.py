# -*- coding: utf-8 -*-
"""音楽・受付中の保留8件（会期に入るツアーが2つある・鶴）を、新しい公演と候補の既存エントリで並べて見比べる（読むだけ・2026-09-15 昼）。
候補＝multi_match_plan_0915.txt でその組み上がりに挙がった既存 id 全部。
見るもの＝新しい公演の名前・会期・会場・枠（飛び先の番号）／既存の名前・会期・会場・ぴあの飛び先
使い方: python tmp/hold_compare_0915.py
出力: tmp/hold_compare_0915.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk01_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk01_0915.json', encoding='utf-8'))}
hold = [int(x) for x in io.open('tmp/hold_uk01_0915.txt', encoding='utf-8').read().split(',') if x.strip()]
plan = io.open('tmp/multi_match_plan_0915.txt', encoding='utf-8').read()
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
split = io.open('tmp/split_built_0915.txt', encoding='utf-8').read()

out = []
for nid in hold:
    b = built[nid]
    m = re.search(r'^👀複数 new%d\s+→ \[([0-9, ]+)\]' % nid, split, re.M)
    ids = [int(x) for x in re.findall(r'\d+', m.group(1))] if m else []
    out.append('=' * 70)
    out.append('new%s %s ｜ %s ｜ %s ｜ %s' % (nid, b.get('name'), b.get('dateLabel'), b.get('venue'), (cands.get(nid) or {}).get('urls')))
    for t in b.get('tickets') or []:
        out.append('   新: %s' % t.get('type'))
    for i in ids:
        e = ev.get(i)
        if not e:
            out.append(' 既存 id%s（もう無い）' % i)
            continue
        out.append(' 既存 id%s %s ｜ %s ｜ %s ｜ genre=%s ｜ pia=%s ｜ 枠%d' % (
            i, e.get('name'), e.get('dateLabel'), (e.get('venue') or '')[:90], e.get('genre'),
            (e.get('links') or {}).get('pia'), len(e.get('tickets') or [])))
io.open('tmp/hold_compare_0915.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('%d件 → tmp/hold_compare_0915.txt' % len(hold))
