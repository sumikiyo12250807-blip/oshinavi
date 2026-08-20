# -*- coding: utf-8 -*-
"""X投稿の候補出し（明日=2026-08-18 発売開始の枠だけ）。
feedback_sale_start_vs_deadline＝date は締切のことが多いので、
「M/D HH:MM発売」と明示された枠 or startDate==対象日 の枠だけを発売開始として拾う。
soldout枠は除く。
"""
import re, json, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

TARGET = "2026-08-18"
MD = "8/18"

raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))

rows = []
for e in EVENTS:
    hits = []
    for t in e.get('tickets') or []:
        if t.get('soldout'):
            continue
        ty = t.get('type') or ''
        explicit = re.search(r'%s\s*\d{1,2}:\d{2}\s*発売' % re.escape(MD), ty)
        if t.get('startDate') == TARGET or explicit:
            hits.append(ty)
    if hits:
        rows.append((e, hits))

print("=== 明日 %s 発売開始の枠を持つエントリ %d件 ===" % (TARGET, len(rows)))
print("ジャンル内訳:", dict(Counter(e.get('genre') for e, _ in rows)))
print()
for e, hits in rows:
    print("id%-5s [%-8s] %s" % (e['id'], e.get('genre'), (e.get('artist') or '')[:44]))
    print("        会場 %s / %s" % ((e.get('venue') or '')[:40], e.get('prefecture')))
    for h in hits:
        print("        - %s" % h)
