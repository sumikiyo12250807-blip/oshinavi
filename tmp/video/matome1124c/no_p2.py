# -*- coding: utf-8 -*-
# すちこ「足が三本ある画像は使わないで」＝卵型の椅子 p2（靴が3つ）を外して8着で書き出し直す
import io, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
s = io.open(D + 'render.py', encoding='utf-8').read()
for a, b in (("ORDER = ['p1', 'p6', 'p7', 'p4', 'p8', 'p2', 'p5', 'p9', 'p3']", "ORDER = ['p1', 'p6', 'p7', 'p4', 'p8', 'p5', 'p9', 'p3']"),
             ("_step = (len(_n)) / 8.0", "_step = (len(_n)) / 7.0"),
             ("for k in range(1, 8)]", "for k in range(1, 7)]"),
             ("[[_url, ORDER[8]]]", "[[_url, ORDER[7]]]")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'render.py', 'w', encoding='utf-8').write(s)
if os.path.exists(D + 'poses/p2.png'):
    os.replace(D + 'poses/p2.png', D + 'poses/p2_3legs.png')
r = subprocess.run([sys.executable, D + 'render.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
io.open(D + 'render_run2.txt', 'w', encoding='utf-8').write('rc %s\n%s\n%s\n' % (r.returncode, r.stdout[-800:], r.stderr[-1000:]))
