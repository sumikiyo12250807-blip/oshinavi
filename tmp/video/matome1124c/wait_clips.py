# -*- coding: utf-8 -*-
# 試し動画2本の書き出しが終わる（clips_1117.txt ができる）まで待つ
import os, time
F = 'C:/Users/user/oshinavi/tmp/video/matome1124c/clips_1117.txt'
while not os.path.exists(F):
    time.sleep(5)
print('done')
