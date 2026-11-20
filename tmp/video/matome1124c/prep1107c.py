# -*- coding: utf-8 -*-
# 11/7：位相が 0.13（〜62秒）→ −0.25（66〜102秒）→ −0.45〜−0.60（106秒〜）と流れる＝1本の格子をやめ、5窓（20秒）の中央値で追う
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
a = "sm = [float(np.median(un))] * len(un)\nout.append('窓の位相"
assert a in s
s = s.replace(a, "sm = [float(np.median(un[max(0, i - 2):i + 3])) for i in range(len(un))]   # 11/7 位相が流れる曲＝5窓の中央値で追う\nout.append('窓の位相", 1)
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'beats_snare.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
io.open(D + 'prep1107c.txt', 'w', encoding='utf-8').write('rc %s %s\n' % (r.returncode, r.stderr[-1500:]) + io.open(D + 'beats_snare.txt', encoding='utf-8').read())
