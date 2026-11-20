# -*- coding: utf-8 -*-
# 全編の書き出し（par_full＝前半・後半を2本同時）。始めたら full_running.flag を作り、終わったら消す（クーザの試しの書き出しはこの印が消えてから）
import io, os, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
io.open(D + 'full_running.flag', 'w', encoding='utf-8').write('お笑い 11/13 後半の書き出し直し中 %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
try:
    r = subprocess.run([sys.executable, D + 'par_half2.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    io.open(D + 'run_full.txt', 'w', encoding='utf-8').write('rc %s\n%s\n%s\n' % (r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
finally:
    os.remove(D + 'full_running.flag')
