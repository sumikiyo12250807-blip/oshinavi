# -*- coding: utf-8 -*-
"""今日のスイープの到達率を数える（[[feedback_newpool_presale_ratio_gate]]）。

「発売前が枯れた」と言う前に、在庫をどれだけ見たかを数字で出す。
ぴあの一覧は1ページ10件なので、期待ページ数 = ceil(total/10)。
到達率が100%でないバケツが1つでもあれば **exit 1**（＝穴埋めの判断材料にしない）。
"""
import math
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
LOG = 'tmp/sweep_presale_0910/_driver.log'

txt = open(LOG, encoding='utf-8').read()
rows = re.findall(r'\[(\S+)\] rc=(\d+) \d+s total=(\d+) pages=(\d+) new=(\S+)', txt)
bad, tot_new = [], 0
print('%-14s %6s %6s %6s %6s  %s' % ('バケツ', 'rc', 'total', 'pages', '期待', '到達率'))
for tag, rc, total, pages, new in rows:
    exp = max(1, math.ceil(int(total) / 10))
    rate = 100.0 * int(pages) / exp
    ok = (rc == '0' and rate >= 99.9)
    if not ok:
        bad.append(tag)
    if new.isdigit():
        tot_new += int(new)
    print('%-14s %6s %6s %6s %6d  %5.1f%% %s' % (tag, rc, total, pages, exp, rate, '' if ok else '🚨'))

print('\nバケツ %d本 / 未掲載候補の延べ %d件' % (len(rows), tot_new))
if bad:
    print('🚨 最終ページまで到達していないバケツ: %s' % ', '.join(bad))
    sys.exit(1)
print('✅ 全バケツが最終ページまで到達（打ち切りゼロ）')
