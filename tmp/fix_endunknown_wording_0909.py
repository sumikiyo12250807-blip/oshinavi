# -*- coding: utf-8 -*-
"""締切が書かれていない枠の日付の行を「M/D HH:MM〜発売中」に直す。
ユーザー修正（2026-09-09）＝「8/1 12:00発売〜」ではなく「8/1 12:00〜発売中」。
index.html renderCard と build_ai_page の両方を揃える。"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

# --- index.html ---------------------------------------------------------
P = 'index.html'
h = io.open(P, encoding='utf-8', newline='').read()
OLD = '      const dateSuffix = endUnknown ? "発売〜" : "";\r\n'
NEW = '      const dateSuffix = endUnknown ? "〜発売中" : "";\r\n'
assert h.count(OLD) == 1, 'index.html の差し込み場所が見つからない'
io.open(P, 'w', encoding='utf-8', newline='').write(h.replace(OLD, NEW))
print('index.html: 「発売〜」→「〜発売中」')

# --- build_ai_page.py ---------------------------------------------------
Q = 'tools/build_ai_page.py'
g = io.open(Q, encoding='utf-8', newline='').read()
OLD2 = '販売中（{t["startDate"]}発売〜・終了日は売り場に記載なし）'
NEW2 = '{t["startDate"]}〜発売中（終了日は売り場に記載なし）'
assert g.count(OLD2) == 1, 'build_ai_page の差し込み場所が見つからない'
io.open(Q, 'w', encoding='utf-8', newline='').write(g.replace(OLD2, NEW2))
print('build_ai_page.py: 同じ言い回しに揃えた')
