# -*- coding: utf-8 -*-
"""tmp/x_extra_check_0911.py の誤検出を3つ直す（2026-09-10 実測）。

① 「A／B／C」判定 … 公演名に「／」が入っているだけの行を羅列と誤判定していた
   （`10:00 クリスマス／アヴェ・マリア エリザベート弦楽アンサンブル／長野` は正しい1行）。
   リスト行（先頭が `HH:MM `）は対象外にする。
② 件数の実数 … 台本は「10の位で切り下げて◯件以上／**10未満はそのままの数**」。
   `9件あるわ` は正しい。**2桁以上の実数だけ**を見る。
③ 締めの一文 … タグ行（#OSHINAVI…）を締めと見ていた。**タグの1つ前の行**が締め。
"""
import io

p = 'tmp/x_extra_check_0911.py'
s = io.open(p, encoding='utf-8').read()

old1 = ("    (re.compile(r'\\d+\\s*件(発売|が発売|の発売|あるわ)'), "
        "'件数の実数を書かない（「他にも◯件以上」だけが例外）'),")
new1 = ("    # 台本＝10未満はそのままの数でよい。2桁以上の実数だけを見る\n"
        "    (re.compile(r'(?<!他にも)\\d{2,}\\s*件(?!以上)(発売|が発売|の発売)'),\n"
        "     '件数の実数を書かない（「他にも◯件以上」だけが例外）'),")
if old1 in s:
    s = s.replace(old1, new1)
    print('② 件数の判定を直した')

old2 = ("    (re.compile(r'^[^\\n]*[／/][^\\n]*[／/][^\\n]*$', re.M), "
        "'「A／B／C」の羅列になっている行がある（1行1公演にする）'),")
new2 = ("    # リスト行（先頭が HH:MM）は公演名に「／」が入るので対象外\n"
        "    (re.compile(r'^(?!\\d{1,2}:\\d{2} )[^\\n]*[／/][^\\n]*[／/][^\\n]*$', re.M),\n"
        "     '「A／B／C」の羅列になっている行がある（1行1公演にする）'),")
if old2 in s:
    s = s.replace(old2, new2)
    print('① 羅列の判定を直した')

old3 = "    tails[f] = lines[-1] if lines else ''"
new3 = ("    # 締めは**タグ行の1つ前**（最終行はいつも #OSHINAVI…）\n"
        "    body = [x for x in lines if x.strip() and not x.strip().startswith('#')]\n"
        "    tails[f] = body[-1] if body else ''")
if old3 in s:
    s = s.replace(old3, new3)
    print('③ 締めの取り方を直した')

io.open(p, 'w', encoding='utf-8').write(s)

import py_compile
py_compile.compile(p, doraise=True)
print('構文OK')
