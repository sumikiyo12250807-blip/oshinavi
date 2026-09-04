# -*- coding: utf-8 -*-
"""tools/x_check.py の「。の直後が改行か」に例外を2つ入れる。

2026-09-04に7本中3本が誤検出になった。3件とも**固有名詞の中の「。」**で、
ここで改行させると名前が壊れる。

  ① リスト行（`時刻 名前／県`）の中の「。」
     例＝「武満徹。～まだ知らない、武満徹。～／東京」
         「Mozu ミニチュア展 ようこそ、ちいさな世界へ。／静岡」
  ② 本文中の「モーニング娘。」＝X_SCRIPT.md が明示している唯一の例外
"""
import io

P = "tools/x_check.py"
s = io.open(P, encoding="utf-8").read()

OLD = '    for m in re.finditer(r"。(?!$)", t):\n        nxt = t[m.end():m.end() + 1]\n'
NEW = (
    '    # 🚨固有名詞の中の「。」は改行させない（改行すると名前が壊れる）。\n'
    '    #   ①リスト行（`時刻 名前／県`）の中 ②本文中の「モーニング娘。」\n'
    '    LISTLINE = re.compile(r"^\\d{1,2}:\\d{2}\\s")\n'
    '    for m in re.finditer(r"。(?!$)", t):\n'
    '        line_start = t.rfind("\\n", 0, m.start()) + 1\n'
    '        if LISTLINE.match(t[line_start:line_start + 6]):\n'
    '            continue\n'
    '        if t[max(0, m.start() - 6):m.end()].endswith("モーニング娘。"):\n'
    '            continue\n'
    '        nxt = t[m.end():m.end() + 1]\n'
)

if "LISTLINE" in s:
    print("すでにパッチ済み")
elif OLD in s:
    io.open(P, "w", encoding="utf-8").write(s.replace(OLD, NEW, 1))
    print("PATCHED")
else:
    print("ABORT: 差し込み位置が見つからない")
    i = s.find('for m in re.finditer(r"。')
    print(repr(s[i - 80:i + 200]))
