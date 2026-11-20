# -*- coding: utf-8 -*-
# 11/18 舞台・トークショー：絵コンテの静止画（場面ごと＋締めの2秒前）→ contact17.png → 試し動画2本（1本ずつ）
#   ①頭 0〜17 秒（前奏・日付・お辞儀→ソファの司会→野球のトーク）②締め 50〜76.1 秒（検索の行→タップ→oshinavi.jp・4人が下りる・最後まで）
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [2.0, 7.0, 10.0, 14.0, 18.5, 21.0, 23.0, 26.0, 31.0, 37.0, 42.5, 47.0, 51.0, 54.0, 58.0, 61.0, 66.0, 70.0, 74.1]
log = []
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-400:]))
r = subprocess.run([sys.executable, D + 'contact17.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('contact rc=%d %s' % (r.returncode, r.stderr[-300:]))
io.open(D + 'board_1118.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
for nm, a, b in (('clip_a', 0.0, 17.0), ('clip_b', 50.0, 76.1)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, (r.stdout + r.stderr).strip()[-300:]))
    io.open(D + 'board_1118.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
io.open(D + 'board_1118.done', 'w').write('done')
