# -*- coding: utf-8 -*-
"""tmp/x_material_0911.py の「2〜3日後の5件」を、同じ組で埋めないようにする。

県を枠ごとにしたら、ツアーの1組が5件の枠を占めるようになった
（佐藤竹善が4行／『スリーゴースト』が3行）。
5件は「大物を並べて見せる」ための枠なので、**同じ組は1件まで**にする。
（明日発売のリストは1件も削らない＝そちらは触らない）
"""
import io

p = 'tmp/x_material_0911.py'
s = io.open(p, encoding='utf-8').read()

old = """        seen2, pick = set(), []
        for x in (big or rs2):
            ln = line(*x)
            if ln in seen2:          # 同じ組・同じ時刻・同じ県は畳む
                continue
            seen2.add(ln)
            pick.append(x)
            if len(pick) >= 5:
                break"""

new = """        # 🚨5件は「大物を並べて見せる」枠なので**同じ組は1件まで**
        #   （県を枠ごとにしたら、ツアーの1組が5件を占めるようになった）
        seen2, pick = set(), []
        for x in (big or rs2):
            key = (x[0].get('artist') or x[0].get('name') or '').strip()
            if key in seen2:
                continue
            seen2.add(key)
            pick.append(x)
            if len(pick) >= 5:
                break"""

assert old in s, 'アンカーが見つからない'
io.open(p, 'w', encoding='utf-8').write(s.replace(old, new))
print('2〜3日後の5件は「同じ組は1件まで」にした')

import py_compile
py_compile.compile(p, doraise=True)
print('構文OK')
