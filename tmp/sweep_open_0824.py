# -*- coding: utf-8 -*-
"""受付中（もう買える枠）をスイープして、発売前だけでは足りない分を埋める（2026-08-24）。

発売前(rlsIn=03)の未掲載が77件しかなく、投入できたのは23件だった。
1バッチ100件が上限（2026-08-21 ユーザー変更）なので、受付中から穴埋めする。

  rlsStatus=0101 … 発売中（先着）
  rlsStatus=0201 … 受付中（抽選）

🚨 受付中は在庫が巨大で、以前「音楽4,318行に対し204ユニークで打ち切り」＝あ行しか見ていない
   という事故を起こしている（feedback_newpool_presale_ratio_gate）。
   ページ到達率を harvest_audit で必ず確認すること。
🚨 出力名は tmp/open_<lg>_0824.json（harvest_audit が open_* を受付中として拾う）。
"""
import subprocess
import sys
import time

STAMP = '0824'
# ジャンル優先順＝①音楽 ②演劇・クラシック ③その他（feedback_harvest_genre_priority）
JOBS = [('01', '音楽', '0101'), ('02', '演劇', '0101'), ('07', 'クラシック', '0101'),
        ('01', '音楽', '0201'), ('02', '演劇', '0201'), ('06', 'イベント', '0101'),
        ('03', 'スポーツ', '0101')]

for lg, name, st in JOBS:
    out = 'tmp/open_%s_%s_%s.json' % (lg, st, STAMP)
    t0 = time.time()
    r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, 'rlsStatus=' + st],
                       capture_output=True)
    tail = r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1:] or ['(出力なし)']
    print('[%s %s %s] exit=%d %.0fs %s' % (lg, name, st, r.returncode, time.time() - t0, tail[0]))
    sys.stdout.flush()
    time.sleep(3)
print('受付中スイープ完了')
