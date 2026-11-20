# -*- coding: utf-8 -*-
# 11/18 タップの場面を撮り直す（11/18 発売のバッジが画面に入るように）→ 設計図 → 54・58 秒の静止画 → 締めの試し動画をもう一度
import io, os, glob, shutil, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
for a in (['shoot_badge.py'], ['make_spec.py']):
    r = subprocess.run([sys.executable, D + a[0]], capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.append('%s rc=%d %s' % (a[0], r.returncode, (r.stdout + r.stderr)[-300:]))
for f in glob.glob(D + 'frames/h_*.png'):
    if os.path.basename(f) in ('h_054.0.png', 'h_058.0.png'):
        os.remove(f)
r = subprocess.run([sys.executable, D + 'render.py', '--frames', '54.0,58.0'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d' % r.returncode)
r = subprocess.run([sys.executable, D + 'contact17.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
r = subprocess.run([sys.executable, D + 'render.py', '--clip', '50.0,76.1'], capture_output=True, text=True, encoding='utf-8', errors='replace')
if os.path.exists(D + 'clip.mp4'):
    shutil.copyfile(D + 'clip.mp4', D + 'clip_b.mp4')
log.append('clip_b rc=%d' % r.returncode)
io.open(D + 'redo_badge.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
