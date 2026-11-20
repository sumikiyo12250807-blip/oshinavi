# -*- coding: utf-8 -*-
# 前回（matome1115o）の .py と出力を新しい順に → recent.txt
import glob, os, io, time
S = 'C:/Users/user/oshinavi/tmp/video/matome1115o/'
L = sorted(glob.glob(S + '*'), key=os.path.getmtime, reverse=True)
out = [time.strftime('%m-%d %H:%M', time.localtime(os.path.getmtime(p))) + ' ' + os.path.basename(p) for p in L if not os.path.isdir(p)][:60]
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/recent.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
