# -*- coding: utf-8 -*-
# 11/16 すちこ「背景がどちらも一緒なのはダメよ」→「2番がいい」＝221717（黒地に赤と青の光の板・暗い）
#   bg.mp4（差し替え済み）→ bg_src.mp4 → 背景のコマ（明るさ・色はそのまま）→ 字を暗い背景の形（白／黄・縁は濃紺）に戻す
#   → 絵コンテの静止画・contact → 試し動画2本（タップ画面は撮り直さない）
import io, os, glob, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
shutil.copyfile(D + 'bg.mp4', D + 'bg_src.mp4')
log = []
def W():
    io.open(D + 'redo_bg.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
r = subprocess.run([sys.executable, D + 'bg_prep.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('bg rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-300:])); W()
ks = io.open(D + 'kara_style.py', encoding='utf-8').read()
x = "        else:     # 11/19 背景 49445 は明るい青いタイル＝字を暗く：まだ＝濃紺／歌った＝えんじ・縁は白の太め＋うっすら影（11/16 主役と同じ）\n            todo, done, stroke, shadow = NAVY, ENJI, WHITE, (0, 0, 0, 70)"
if x in ks:
    ks = ks.replace(x, "        else:     # 11/19 背景 221717（黒地に赤と青の光の板・暗い）＝白／黄・縁は濃紺（暗い背景のいつもの形・11/18 舞台 21865 と同じ）\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)")
    io.open(D + 'kara_style.py', 'w', encoding='utf-8').write(ks)
log.append('kara_style 白／黄に戻した %s' % ('WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)\n' in ks.split('11/19 背景 221717')[1][:200] if '11/19 背景 221717' in ks else False)); W()
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
T = [0.0, 5.0, 9.0, 15.0, 21.0, 24.0, 27.0, 33.0, 39.0, 43.0, 46.0, 51.0, 54.0, 58.0, 63.0, 67.0, 74.0, 80.0, 84.0, 90.0, 94.0]
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in T)], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('frames rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-300:])); W()
r = subprocess.run([sys.executable, D + 'contact17.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('contact rc=%d %s' % (r.returncode, r.stderr[-300:])); W()
for nm, a, b in (('clip_a', 0.0, 17.0), ('clip_b', 72.0, 96.02)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if os.path.exists(D + 'clip.mp4'):
        shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s rc=%d %.0f 秒' % (nm, r.returncode, time.time() - t0)); W()
r = subprocess.run([sys.executable, D + 'mk_page_1119.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.append('page rc=%d %s' % (r.returncode, (r.stdout + r.stderr)[-300:])); W()
io.open(D + 'redo_bg.done', 'w').write('done')
