# -*- coding: utf-8 -*-
# 11/17：背景のコマ（元の明るさ・色のまま）→ テンポの当たり → prep1117a.txt
import io, os, subprocess, sys
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1117a.txt', 'w', encoding='utf-8')
for f in ('bg_prep.py', 'tempo_check.py'):
    r = subprocess.run([sys.executable, D + f], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (f, r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
    out.flush()
out.close()
