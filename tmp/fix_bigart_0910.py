# -*- coding: utf-8 -*-
"""check_big_artists.py に紛れ込んだ「実改行になった \\n」を1行に戻す。

heredoc 経由で書いたときに \\n がそのまま改行になってしまい、
Python の文字列リテラルが行の途中で切れて SyntaxError になっていた。
"""
import io

BACKSLASH_N = chr(92) + 'n'
p = 'tools/check_big_artists.py'
s = io.open(p, encoding='utf-8').read()

broken = "        print('\n=== 載っているが、この窓に発売が始まる枠が無い %d件 ===' % len(gap))"
fixed = ("        print('" + BACKSLASH_N
         + "=== 載っているが、この窓に発売が始まる枠が無い %d件 ===' % len(gap))")

if broken in s:
    s = s.replace(broken, fixed)
    print('print行を直した')
else:
    print('print行は既に正しい')

io.open(p, 'w', encoding='utf-8').write(s)

# 構文チェック
import py_compile
try:
    py_compile.compile(p, doraise=True)
    print('構文OK')
except py_compile.PyCompileError as e:
    print('まだ壊れている:', e)
