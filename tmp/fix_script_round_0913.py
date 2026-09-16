# -*- coding: utf-8 -*-
"""X_SCRIPT.md の「丸め方」をユーザーの言うとおり（四捨五入）に直す（2026-09-13）。
🚨台本が正なのに、要約や古い版のまま動くと同じ間違いを繰り返す
（memory feedback_rules_one_place_and_fix_summaries）。
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = 'X_SCRIPT.md'
s = io.open(p, encoding='utf-8', newline='').read()

lines = s.split('\n')
out, i, done = [], 0, False
while i < len(lines):
    ln = lines[i]
    if not done and '丸め方＝10の位で切り下げて' in ln:
        indent = ln[:len(ln) - len(ln.lstrip())]
        out += [
            indent + '🚨**丸め方＝四捨五入（2026-09-13 ユーザー修正・これが最新）**。',
            indent + '**下1桁が0〜4なら切り下げて「◯件以上」／5〜9なら切り上げて「◯件近く」。**',
            indent + 'ユーザーの言葉「**切り下げってなに？　11件なら10件以上　15件以上なら20件近く**」。',
            indent + '例＝残り11件→「**10件以上**」／残り14件→「**10件以上**」／残り15件→「**20件近く**」／',
            indent + '　　残り35件→「**40件近く**」／残り129件→「**130件近く**」。',
            indent + '**10未満はそのままの数**（残り1件→「他にも1件あるわ」／残り5件→「他にも5件あるわ」）。',
            indent + '⛔旧「10の位で切り下げ・『◯件近く』は使わない」（2026-09-09〜09-12）は**失効**。',
        ]
        # 旧文の4行（切り下げ／近く禁止／例／10未満）を飛ばす
        i += 4
        done = True
        continue
    out.append(ln)
    i += 1

assert done, '目印の行が見つからない'
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(out))
print('X_SCRIPT.md を直したわ')
