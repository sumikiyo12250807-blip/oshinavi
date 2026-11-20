# -*- coding: utf-8 -*-
# 11/3：背景のコマ（73197 夜の街の灯り＝明るく細かい→強めにぼかして暗く）・bg_video のループ長 20 秒・tempo_check
import io, os, re, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep4.txt', 'w', encoding='utf-8')
s = io.open(D + 'bg_prep.py', encoding='utf-8').read()
s = re.sub(r"vf = '.*?'", "vf = 'scale=-2:1920:flags=lanczos,crop=1080:1920,gblur=sigma=7,eq=brightness=-0.22:saturation=0.9'", s)
io.open(D + 'bg_prep.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'bg_video.py', encoding='utf-8').read()
s = s.replace('FPS, L, XF = 30.0, 30.0, 0.5', 'FPS, L, XF = 29.97, 19.9, 0.6')
io.open(D + 'bg_video.py', 'w', encoding='utf-8').write(s)
for f in ('bg_prep.py', 'tempo_check.py'):
    r = subprocess.run([sys.executable, D + f], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (f, r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
out.close()
