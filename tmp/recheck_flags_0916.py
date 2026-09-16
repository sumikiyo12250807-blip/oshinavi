# -*- coding: utf-8 -*-
"""compare_recheck_0916.md から、ジャンル以外のズレ（千秋楽・県・枠・中止等）を「読めた件」と「読めなかった件」に分けて数える（読むだけ）。
使い方: python tmp/recheck_flags_0916.py
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
txt = io.open('tmp/compare_recheck_0916.md', encoding='utf-8').read()
blocks = re.findall(r'- \*\*id(\d+) (.*?)\*\*.*?\n((?:  - .*\n)*)', txt)
clean, noted = [], []
for i, name, body in blocks:
    flags = [ln[4:] for ln in body.splitlines() if ln.startswith('  - ') and not ln.startswith('  - ジャンル')]
    has_note = any(f.startswith('note') for f in flags)
    real = [f for f in flags if not f.startswith('note')]
    if not real and not has_note:
        continue
    (noted if has_note else clean).append((int(i), name, real))
print('読めた件でジャンル以外のズレ %d件 ／ 読めなかった件 %d件' % (len(clean), len(noted)))
for i, name, real in clean:
    print('  id%d %s ｜ %s' % (i, name[:30], ' ／ '.join(real)))
print('読めなかった id:', ','.join(str(i) for i, _, _ in noted))
