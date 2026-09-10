# -*- coding: utf-8 -*-
"""21時すぎまで待ってから、隠れ枠ヒールの --build を回す。

🚨自分を呼び戻すための背景タイマー（[[feedback_noon_heal_missed_twice]]＝時計を叩く）。
今日の当日発売の残り＝パーカーズ21:00・広瀬香美18:00。21:00発売の後でないと締切が出ない。
"""
import datetime
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

TARGET = datetime.datetime.now().replace(hour=21, minute=8, second=0, microsecond=0)
wait = (TARGET - datetime.datetime.now()).total_seconds()
if wait > 0:
    print('%s まで待つ（%d秒）' % (TARGET.strftime('%H:%M'), wait))
    time.sleep(wait)

print('=== heal_stale_deadlines --build 開始 %s' % datetime.datetime.now().strftime('%H:%M'))
r = subprocess.run([sys.executable, 'tools/heal_stale_deadlines.py', '--build'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout[-6000:])
if r.stderr:
    print('--- stderr ---')
    print(r.stderr[-2000:])
print('=== 終了 rc=%d %s' % (r.returncode, datetime.datetime.now().strftime('%H:%M')))
