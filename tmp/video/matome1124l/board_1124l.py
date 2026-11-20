# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ：タップ画面を撮る → 絵コンテの静止画（0秒のカバー・場面ごと・締め）→ 試し動画2本（頭 0〜30 秒／締め 66〜97 秒）
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124l/'
log = []
def W():
    io.open(D + 'board_1124l.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('badge rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-600:])); W()
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [0.0, 2.0, 4.5, 7.5, 10.5, 12.5, 15.0, 18.0, 20.5, 24.0, 27.0, 29.5, 33.5, 36.0, 39.0, 42.0, 44.5, 47.0, 50.5]
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-1500:])); W()
for nm, a, b in (('clip_a', 0.0, 25.0), ('clip_b', 26.0, 51.6)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, (r.stdout + r.stderr).strip()[-300:])); W()
io.open(D + 'board_1124l.done', 'w').write('done')
