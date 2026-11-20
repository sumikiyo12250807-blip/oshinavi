# -*- coding: utf-8 -*-
# 11/17 J-POP の試し動画2本を1本ずつ（同時に回さない）：①頭 0〜15.5 秒（前奏・日付・金のダンス→向きを変える→エレキの子）
#   ②締め 46.5〜60.9 秒（検索の行→タップの場面→「oshinavi.jp なのよ」・4人が下りる・最後まで）→ clip_a.mp4・clip_b.mp4
import io, os, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
for nm, a, b in (('clip_a', 0.0, 15.5), ('clip_b', 46.5, 60.9)):
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]))
io.open(D + 'clips_1117.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
