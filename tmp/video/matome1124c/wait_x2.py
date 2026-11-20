# -*- coding: utf-8 -*-
# x_2pass.txt ができるまで待つ（最長 170 秒）
import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
t0 = time.time()
while time.time() - t0 < 170 and not os.path.exists(D + 'x_2pass.txt'):
    time.sleep(5)
print(open(D + 'x_2pass.txt', encoding='utf-8').read() if os.path.exists(D + 'x_2pass.txt') else 'まだ')
