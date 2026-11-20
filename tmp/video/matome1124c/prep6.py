# -*- coding: utf-8 -*-
# 11/3：タップ場面の本物の画面＝爆笑問題カーボーイ30周年ライブ（30903・2次受付 11/3 19:00発売）を前の夜 11/2 20:00 の時計で撮る
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
s = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
for a, b in (("CID, Q, MD = 40935, '囲碁将棋', '11/2'", "CID, Q, MD = 30903, '爆笑問題', '11/3'"), ('new D(2026,10,1,20,0)', 'new D(2026,10,2,20,0)')):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(r.returncode, r.stdout[-1500:], r.stderr[-1500:])
