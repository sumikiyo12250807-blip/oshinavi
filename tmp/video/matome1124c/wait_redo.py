# -*- coding: utf-8 -*-
# redo_bg.done か contact の段を待つ（最長 170 秒）
import os, sys, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
key = sys.argv[1] if len(sys.argv) > 1 else 'done'
t0 = time.time()
def ok():
    if os.path.exists(D + 'redo_bg.done'):
        return True
    return key == 'contact' and os.path.exists(D + 'redo_bg.txt') and 'contact rc' in open(D + 'redo_bg.txt', encoding='utf-8').read()
while time.time() - t0 < 170 and not ok():
    time.sleep(5)
print(open(D + 'redo_bg.txt', encoding='utf-8').read() if os.path.exists(D + 'redo_bg.txt') else 'まだ')
