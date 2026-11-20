# -*- coding: utf-8 -*-
# tiktok_hq.txt ができるまで待つ（最長 170 秒）
import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
t0 = time.time()
while time.time() - t0 < 170 and not os.path.exists(D + 'tiktok_hq.txt'):
    time.sleep(5)
print(open(D + 'tiktok_hq.txt', encoding='utf-8').read() if os.path.exists(D + 'tiktok_hq.txt') else 'まだ')
