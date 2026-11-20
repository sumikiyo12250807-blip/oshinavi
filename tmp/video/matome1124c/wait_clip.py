# -*- coding: utf-8 -*-
# 試し動画の書き出しが終わる（clip_then_full.txt に 1 本目の rc が出る）まで待つ
import os, time
F = 'C:/Users/user/oshinavi/tmp/video/matome1124c/clip_then_full.txt'
for _ in range(900):
    if os.path.exists(F):
        s = open(F, encoding='utf-8').read()
        if s.count('rc ') >= 1:
            print(s[:1500])
            break
    time.sleep(2)
