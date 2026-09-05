# -*- coding: utf-8 -*-
"""dup3 の県名正規化バグを直す＝「京都」から都を剥がして「京」にしていた。"""
import io
P = 'tmp/dup3_0905.py'
s = io.open(P, encoding='utf-8').read()
OLD = "        for m in RE_SLOT.finditer(t.get('type') or ''):\n            pref = re.sub(r'[都府県]$', '', m.group(1))\n"
NEW = ("        for m in RE_SLOT.finditer(t.get('type') or ''):\n"
       "            pref = m.group(1)\n"
       "            if pref not in PREF_SET:\n"
       "                pref = re.sub(r'[都府県]$', '', pref)\n")
assert OLD in s, 'target not found'
s = s.replace(OLD, NEW, 1)
s = s.replace("RE_SLOT = re.compile(", "PREF_SET = set(PREF.split('|'))\nRE_SLOT = re.compile(", 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('PATCHED')
