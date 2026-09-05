# -*- coding: utf-8 -*-
"""split_batch2 に id5766 EPO を足す。

「公演は全部載っている」6件のうち EPO だけ、**東京9/29の枠が足りていなかった**：
  既存（ぴあ）＝一般発売〜9/13 23:59 の1枠だけ
  e+          ＝〜9/20 18:00 と 〜9/25 18:00 の2枠
つまり 9/13 を過ぎると画面上は買えないのに、実際は e+ でまだ買える状態だった。
→ 足りない枠だけ足す（既存の枠は触らない）。
"""
import io

P = 'tmp/split_batch2_0905.py'
s = io.open(P, encoding='utf-8').read()

OLD = "SAME = [6960, 6965, 6976, 6981, 6984, 6987]\nMERGE = {6958: 5879, 6980: 5251, 6989: 3892, 6994: 579}\n"
NEW = ("SAME = [6960, 6965, 6976, 6981, 6984]\n"
       "MERGE = {6958: 5879, 6980: 5251, 6989: 3892, 6994: 579, 6987: 5766}\n"
       "# EPO だけは公演が全部載っているが**枠**が足りない（東京9/29が既存1枠 / e+2枠）。\n"
       "# 公演の重なりで判定すると足す枠が0本になるので、窓の終わりが既存より後の枠は足す。\n"
       "SLOT_LEVEL = {5766}\n")
assert OLD in s, 'target1'
s = s.replace(OLD, NEW, 1)

OLD2 = "    add = [t for t in b['tickets'] if key(t) and not (key(t) & have)]\n"
NEW2 = ("    if tid in SLOT_LEVEL:\n"
        "        # 公演ごとに「既存の窓の終わりの最大」より後まで買える枠だけ足す\n"
        "        last = {}\n"
        "        for t in (e.get('tickets') or []):\n"
        "            for k in key(t):\n"
        "                last[k] = max(last.get(k, ''), t.get('date') or '')\n"
        "        add = [t for t in b['tickets']\n"
        "               if key(t) and all((t.get('date') or '') > last.get(k, '') for k in key(t))]\n"
        "    else:\n"
        "        add = [t for t in b['tickets'] if key(t) and not (key(t) & have)]\n")
assert OLD2 in s, 'target2'
s = s.replace(OLD2, NEW2, 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('PATCHED')
