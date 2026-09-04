# -*- coding: utf-8 -*-
"""id2254 のぴあ実ページの販売スケジュール行を「買える／買えない」で仕分ける。

`tmp/count_2254_0905.txt` に落としてある行を読み直すのではなく、
実ページをもう一度叩かずに済むよう、その出力から行を取り出して数える。

買える＝「販売期間中」「受付中」「発売前」「まもなく抽選受付」
買えない＝「予定枚数終了」「受付終了」「販売終了」「抽選受付終了」
"""
import io, re

SRC = 'tmp/count_2254_0905.txt'
OK = ('販売期間中', '受付中', '発売前', 'まもなく抽選受付')
NG = ('予定枚数終了', '抽選受付終了', '受付終了', '販売終了')

rows, cur = [], None
for ln in io.open(SRC, encoding='utf-8'):
    m = re.match(r'\s{2}(https://t\.pia\.jp/\S+)', ln)
    if m:
        cur = m.group(1)
        continue
    m = re.match(r'\s{6}- (.+)$', ln)
    if m and cur:
        rows.append((cur, m.group(1).strip()))

buy, dead, other = [], [], []
for u, t in rows:
    if any(k in t for k in NG):
        dead.append((u, t))
    elif any(k in t for k in OK):
        buy.append((u, t))
    else:
        other.append((u, t))

out = io.open('tmp/classify_2254_0905.txt', 'w', encoding='utf-8')
out.write('ぴあの販売スケジュール行 %d件 ＝ 買える %d / 買えない %d / どちらとも言えない %d\n\n'
          % (len(rows), len(buy), len(dead), len(other)))
out.write('--- 買える行 ---\n')
for u, t in buy:
    out.write('  %s\n     %s\n' % (t[:190], u))
out.write('\n--- どちらとも言えない行 ---\n')
for u, t in other:
    out.write('  %s\n     %s\n' % (t[:190], u))
out.close()
print('ROWS=%d BUY=%d DEAD=%d OTHER=%d' % (len(rows), len(buy), len(dead), len(other)))
