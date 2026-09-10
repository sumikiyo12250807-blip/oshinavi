# -*- coding: utf-8 -*-
"""tmp/x_material_0911.py を2点直す。

① 県は**その枠の県**（バッジの type に入っている）を使う。
   エントリの prefecture を使うと、ツアーだと全県が並んで
   「その県も明日発売」と誤読される（2026-09-10 に春風亭昇太で実際に起きた）。
② 「他にも◯件」＝10の位で切り下げて「◯件以上」。**10未満はそのままの数**で「以上」を付けない。
"""
import io

BS_N = chr(92) + 'n'          # バックスラッシュ + n の2文字
p = 'tmp/x_material_0911.py'
s = io.open(p, encoding='utf-8').read()

old1 = """def line(e, t):
    nm = (e.get('artist') or e.get('name') or '').strip()
    pref = (e.get('prefecture') or '').strip()"""
new1 = """PREF_IN_TYPE = re.compile(r'（([^）0-9]+?)\\s*(?:R[0-9]+年\\s*)?[0-9]{1,2}/[0-9]{1,2}')


def line(e, t):
    nm = (e.get('artist') or e.get('name') or '').strip()
    # 🚨県は**その枠の県**を使う。エントリの prefecture だとツアーで全県が並び、
    #   「その県も明日発売」と誤読される（2026-09-10 春風亭昇太で実際に起きた）
    m = PREF_IN_TYPE.search(t.get('type') or '')
    pref = (m.group(1).strip() if m else (e.get('prefecture') or '').strip())"""

if old1 in s:
    s = s.replace(old1, new1)
    print('① 県を枠から取るようにした')
else:
    print('① すでに直っている')

old2 = "            w('他にも%d件以上" + BS_N + "' % floor10(rest))"
new2 = ("            # 台本＝10の位で切り下げて「◯件以上」。**10未満はそのままの数**\n"
        "            w('他にも%d件%s" + BS_N + "' % (floor10(rest), '以上' if rest >= 10 else ''))")

if old2 in s:
    s = s.replace(old2, new2)
    print('② 10未満は「以上」を付けないようにした')
else:
    print('② アンカーが見つからない（要確認）')

io.open(p, 'w', encoding='utf-8').write(s)

import py_compile
try:
    py_compile.compile(p, doraise=True)
    print('構文OK')
except py_compile.PyCompileError as e:
    print('壊れた:', e)
