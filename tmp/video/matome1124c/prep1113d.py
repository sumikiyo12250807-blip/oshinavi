# -*- coding: utf-8 -*-
# タップ画面の時計を 11/12 20:00 → 11/10 20:00 に（TikTok は 11/10 の夜から見られる＝「明日発売」と出さない）→ 撮り直し → 締めの試し動画を出し直し・締めの所のコマ
import io, os, re, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1113d.txt', 'w', encoding='utf-8')
sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
assert 'new D(2026,10,12,20,0)' in sb
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb.replace('new D(2026,10,12,20,0)', 'new D(2026,10,10,20,0)'))
for a in (['shoot_badge.py'], ['render.py', '--frames', '83.8,105.0'], ['render.py', '--clip', '86.5,101.0']):
    r = subprocess.run([sys.executable, D + a[0]] + a[1:], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (a, r.returncode, r.stdout[-1500:], r.stderr[-1500:])); out.flush()
shutil.copyfile(D + 'clip.mp4', D + 'clip_end.mp4')
out.close()
