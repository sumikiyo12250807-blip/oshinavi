# -*- coding: utf-8 -*-
# 11/19 クラシック：タップ画面を撮る → 絵コンテの静止画（0秒のカバー・場面ごと・締めの2秒前）→ 試し動画2本（頭 0〜17 秒／締め 72〜96 秒）
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
def W():
    io.open(D + 'board_1119.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
r = subprocess.run([sys.executable, D + 'shoot_badge.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('badge rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-600:])); W()
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [0.0, 5.0, 9.0, 15.0, 21.0, 24.0, 27.0, 33.0, 39.0, 43.0, 46.0, 51.0, 54.0, 58.0, 63.0, 67.0, 74.0, 80.0, 84.0, 90.0, 94.0]
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-1500:])); W()
for nm, a, b in (('clip_a', 0.0, 17.0), ('clip_b', 72.0, 96.02)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, (r.stdout + r.stderr).strip()[-300:])); W()
io.open(D + 'board_1119.done', 'w').write('done')
