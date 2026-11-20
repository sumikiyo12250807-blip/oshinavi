# -*- coding: utf-8 -*-
# 18人を3人ずつ6枚の点検画像にする
import subprocess, sys
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
G = [['g1', 'g2', 'g3'], ['g4', 'g5', 'g6'], ['g7', 'g8', 'g9'], ['c1', 'c2', 'c3'], ['c4', 'c5', 'c6'], ['c7', 'c8', 'c9']]
for i, g in enumerate(G):
    subprocess.run([sys.executable, D + 'look_pose2.py', ','.join(g), 'look%d' % i])
