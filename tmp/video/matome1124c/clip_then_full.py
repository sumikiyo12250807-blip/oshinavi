# -*- coding: utf-8 -*-
# 11/4：試し動画（8〜20秒）→ 続けて全部の書き出し（OKが出たらすぐ使えるように先に回しておく・直しが来たら作り直す）
import os, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = open(D + 'clip_then_full.txt', 'w', encoding='utf-8')
for args in (['--clip', '8,20'], []):
    log.write('start %s %s\n' % (args, datetime.datetime.now().strftime('%H:%M:%S'))); log.flush()
    r = subprocess.run([sys.executable, D + 'render.py'] + args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.write('rc %s %s\n%s\n%s\n' % (r.returncode, datetime.datetime.now().strftime('%H:%M:%S'), r.stdout[-600:], r.stderr[-1200:])); log.flush()
log.close()
