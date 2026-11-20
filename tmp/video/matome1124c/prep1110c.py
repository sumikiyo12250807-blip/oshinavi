# -*- coding: utf-8 -*-
# 11/10 第2版の拍：131.66BPM（スネアだけの1位）は位相が 0.21→0.88 秒まで流れた。tempo1110 で測り直すと 133.0〜133.25 が
#   スネア 2.27／キック 3.04 で位相の流れ幅 0.14（いちばん揃う）＝tempo_check のキック 133.2 と同じ → 132.9〜133.3 に絞って作り直す
#   → beats.json → 絵コンテ → 試し動画（47.5〜58.8 秒）
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1110c.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
    out.flush()
    return r.returncode


s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
assert 'np.arange(131.0, 134.01, 0.02)' in s
s = s.replace('np.arange(131.0, 134.01, 0.02)', 'np.arange(132.9, 133.31, 0.02)')   # 11/10 第2版
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
run('beats_snare.py')
out.write(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '47.5,58.8')
out.close()
open(D + 'prep1110c.done', 'w').close()
