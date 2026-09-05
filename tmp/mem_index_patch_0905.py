# -*- coding: utf-8 -*-
"""MEMORY.md の要約行を本文に合わせて直す（e+ 側の同型事故を追記した分）。"""
import io

P = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/MEMORY.md'
s = io.open(P, encoding='utf-8').read()

OLD = ('🚨 [harvestは既存artist名だけで除外→同名の別公演を拾えない]'
       '(feedback_harvest_name_dedup_blindspot.md)（2026-08-17にeventCd判定へ修正済）')
NEW = ('🚨🚨 [ハーベストの重複判定を「名前」でやると巻き添えで消える]'
       '(feedback_harvest_name_dedup_blindspot.md)'
       '（ぴあは2026-08-17・**e+は2026-09-05にeventCd判定へ修正**＝36候補が2件まで落ちていた）')

assert OLD in s, 'index line not found'
io.open(P, 'w', encoding='utf-8', newline='\n').write(s.replace(OLD, NEW, 1))
print('INDEX_PATCHED')
