# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の振り分け下書きを作る（読むだけ・2026-09-14 朝）。assign_plan_0913.py の日付違い。
決まり＝ぴあのサブカテゴリ(_piaSub)を PIA_GENRE_MAP で機械で写す（memory feedback_genre_pia_asis_and_other）。
_genre（投入時の下書き）と突き合わせて、食い違う子・行き先が無い子を洗い出す。
使い方: python tmp/assign_plan_0914.py
出力: tmp/assign_plan_0914.txt
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')

from build_pia_entries import PIA_GENRE_MAP  # noqa: E402

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
new = [e for e in ev if e.get('genre') == 'new']

lines = []
mismatch = []
nosub = []
for e in sorted(new, key=lambda x: x['id']):
    sub = (e.get('_piaSub') or '')
    leaf = sub.split('/')[-1] if sub else ''
    hit = PIA_GENRE_MAP.get(leaf)
    mapped = hit[0] if hit else None
    draft = e.get('_genre')
    mark = 'OK ' if mapped and mapped == draft else '⚠️ '
    if not sub:
        nosub.append(e)
        mark = '❓ '
    elif mapped != draft:
        mismatch.append((e, mapped, draft))
    lines.append('%sid%-5s %-14s draft=%-10s map=%-10s %s | %s' % (
        mark, e['id'], leaf, draft, mapped, (e.get('name') or '')[:34], (e.get('links') or {}).get('pia') or ''))

head = [
    '=== 新着プール %d件の振り分け下書き（ぴあの_piaSubを機械で写す）===' % len(new),
    '一致 %d件 / 食い違い %d件 / _piaSub無し %d件' % (
        len(new) - len(mismatch) - len(nosub), len(mismatch), len(nosub)),
    '',
]
io.open('tmp/assign_plan_0914.txt', 'w', encoding='utf-8').write('\n'.join(head + lines) + '\n')
print('\n'.join(head[:2]))
for e, mapped, draft in mismatch:
    print('  食い違い id%s %s: draft=%s map=%s (%s)' % (e['id'], e.get('_piaSub'), draft, mapped, (e.get('name') or '')[:30]))
for e in nosub:
    print('  _piaSub無し id%s %s' % (e['id'], (e.get('name') or '')[:30]))
