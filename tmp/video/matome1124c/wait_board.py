# -*- coding: utf-8 -*-
# board_1119 が終わるか、frames の段が終わるまで待つ（最長 9 分）
import os, sys, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
key = sys.argv[1] if len(sys.argv) > 1 else 'done'
t0 = time.time()
while time.time() - t0 < 540:
    if os.path.exists(D + 'board_1119.done'):
        break
    if key == 'frames' and os.path.exists(D + 'board_1119.txt') and 'frames rc' in open(D + 'board_1119.txt', encoding='utf-8').read():
        break
    time.sleep(10)
print(open(D + 'board_1119.txt', encoding='utf-8').read() if os.path.exists(D + 'board_1119.txt') else 'まだ')
