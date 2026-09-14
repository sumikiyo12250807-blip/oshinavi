# -*- coding: utf-8 -*-
"""push前の照合（--new・--ids）で「混雑ページで読めなかった（FETCH）」「登録にあるのにぴあの買える枠に無い（STALE）」が
出たエントリの id を拾い、1本だけで照合し直すための一覧を作る（2026-09-14 夜）。
2本同時に照合を回したせいで ぴあが混雑ページ（sorry.pia.jp）を返した＝STALE の多くは読めなかった巻き添え。
  除く＝8693（今日18:00締切の枠＝締切が過ぎただけ・明日の朝の削除ルート）／7946（無効URL＝お疲れ様で聞く件）
       3501（今日11:00締切の抽選＝今夜で外れる）／4272（発売日の無い枠＝明日の朝）
使い方: python tmp/recheck_ids_2133_0914.py  → tmp/recheck_ids_2133_0914.txt（カンマ区切り）
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SKIP = {8693, 7946, 3501, 4272}
ids = []
for f in ('tmp/reconcile_new_2133_0914.txt', 'tmp/reconcile_ids_2133_0914.txt'):
    cur = None
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'^\S+ id=(\d+) ', line)
        if m:
            cur = int(m.group(1))
            continue
        if cur and re.search(r'(❌FETCH|💤STALE)', line) and cur not in SKIP and cur not in ids:
            ids.append(cur)
io.open('tmp/recheck_ids_2133_0914.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in ids))
print('%d件: %s' % (len(ids), ','.join(str(i) for i in ids)))
