# -*- coding: utf-8 -*-
# final_1119.done を待つ（最長 170 秒）
import os, time
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
t0 = time.time()
while time.time() - t0 < 170 and not os.path.exists(D + 'final_1119.done'):
    time.sleep(5)
print('done' if os.path.exists(D + 'final_1119.done') else 'まだ', open(D + 'par_full.txt', encoding='utf-8', errors='replace').read()[-300:] if os.path.exists(D + 'par_full.txt') else '')
