# -*- coding: utf-8 -*-
# 前半 raw1.mp4 が途中で止まって壊れた（moov なし）＝前半だけ書き出し直す → finish_1115.py（つなぐ・仕上げ・Downloads へ）
import os, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = open(D + 'redo_raw1.txt', 'w', encoding='utf-8')
log.write('start %s\n' % datetime.datetime.now().strftime('%H:%M:%S')); log.flush()
if os.path.exists(D + 'raw1.mp4'):
    os.replace(D + 'raw1.mp4', D + 'raw1_broken.mp4')
r = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '0.000,52.259', '--out', D + 'raw1.mp4'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('raw1 rc %d %s %s\n' % (r.returncode, datetime.datetime.now().strftime('%H:%M:%S'), r.stderr[-400:])); log.flush()
r = subprocess.run([sys.executable, D + 'finish_1115.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('finish rc %d %s\n' % (r.returncode, r.stderr[-400:]))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
