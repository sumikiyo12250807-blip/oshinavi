# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ：タップ画面を撮る → 絵コンテの静止画（0秒のカバー・場面ごと・締め）→ 試し動画2本（頭 0〜30 秒／締め 66〜97 秒）
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
def W():
    io.open(D + 'board_1124c.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('badge rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-600:])); W()
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [0.0, 3.5, 8.0, 14.0, 19.5, 23.0, 26.5, 30.0, 33.0, 36.5, 39.5, 42.0, 48.0, 51.0, 54.0, 58.0, 61.0, 64.0, 67.0, 72.0, 77.0, 80.0, 84.0, 88.0, 92.0, 96.5]
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-1500:])); W()
for nm, a, b in (('clip_a', 0.0, 30.0), ('clip_b', 66.0, 97.0)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, (r.stdout + r.stderr).strip()[-300:])); W()
io.open(D + 'board_1124c.done', 'w').write('done')
