# -*- coding: utf-8 -*-
# render.txt（書き出しの最後に書く）が出るまで待つ＝最大9分
import os, time
P = 'C:/Users/user/oshinavi/tmp/video/matome1124c/render.txt'
for i in range(108):
    if os.path.exists(P):
        print('ready', open(P, encoding='utf-8').read())
        break
    time.sleep(5)
else:
    print('still running')
