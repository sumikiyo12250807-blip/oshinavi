# -*- coding: utf-8 -*-
# 11/10 第4版の拍（beats_kick2＝キックの位相を追う・当たり スネア 3.27／キック 4.86）で絵コンテと試し動画（47.5〜58.8 秒）を出し直す
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1110d.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
    out.flush()
    return r.returncode


run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '47.5,58.8')
out.close()
open(D + 'prep1110d.done', 'w').close()
