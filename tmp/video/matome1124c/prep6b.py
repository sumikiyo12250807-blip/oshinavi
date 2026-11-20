# -*- coding: utf-8 -*-
# 11/4：タップ場面の本物の画面＝金属・黒帯のダルガラミ（42825・一般 11/4 10:00発売）を前の夜 11/3 20:00 の時計で撮る
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
s = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
for a, b in (("CID, Q, MD = 30903, '爆笑問題', '11/3'", "CID, Q, MD = 42825, '金属バット', '11/4'"), ('new D(2026,10,2,20,0)', 'new D(2026,10,3,20,0)')):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(r.returncode, r.stdout[-1500:], r.stderr[-1500:])
