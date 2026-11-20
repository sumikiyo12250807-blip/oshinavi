# -*- coding: utf-8 -*-
# render.txt（out_x.mp4 を作った印）が出るまで待つ（最大 9 分）
import os, time
p = 'C:/Users/user/oshinavi/tmp/video/matome1124c/render.txt'
t0 = os.path.getmtime(p) if os.path.exists(p) else 0
for _ in range(108):
    if os.path.exists(p) and os.path.getmtime(p) > t0:
        print('done'); break
    time.sleep(5)
else:
    print('still running')
