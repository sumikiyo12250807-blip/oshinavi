# -*- coding: utf-8 -*-
# 主役の書き出し（shuyaku1115/par14.done）が終わってから J-POP の全編を書き出す（重い書き出しを重ねない）
import os, subprocess, sys, time, io
os.chdir('C:/Users/user/oshinavi')
while not os.path.exists('tmp/video/shuyaku1115/par14.done'):
    time.sleep(30)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, 'tmp/video/matome1124c/render.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
io.open('tmp/video/matome1124c/render_full.txt', 'w', encoding='utf-8').write('rc=%d\n%s\n%s' % (r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
