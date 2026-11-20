# -*- coding: utf-8 -*-
# board_1119.done を待つ（最長 170 秒・前景で待てる長さ）
import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
t0 = time.time()
while time.time() - t0 < 170 and not os.path.exists(D + 'board_1119.done'):
    time.sleep(5)
print('done' if os.path.exists(D + 'board_1119.done') else 'まだ')
