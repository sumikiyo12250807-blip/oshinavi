# -*- coding: utf-8 -*-
# 試し動画2本を1本ずつ（同時に回さない）：①歌い出し 9.5〜24.5 秒（名前の塊の入れ替え・歩く子2人の入れ替わり）②締め 95.0〜109.3 秒（OSHINAVI.jp・後奏で4人が下りる・最後の2秒）
#   → clip_a.mp4・clip_b.mp4、かかった秒も記録（全編の書き出し時間の見込み）
import io, os, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = []
for nm, a, b in (('clip_a', 9.0, 24.0), ('clip_b', 60.0, 75.6)):   # 11/16 TikTok：①名前の所 ②タップ→締め→後奏（最後まで）
    t0 = time.time()
    r = subprocess.run([sys.executable, D + 'render.py', '--clip', '%s,%s' % (a, b)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    shutil.copyfile(D + 'clip.mp4', D + nm + '.mp4')
    log.append('%s %.1f〜%.1f 秒 rc=%d %.0f 秒かかった %s' % (nm, a, b, r.returncode, time.time() - t0, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]))
io.open(D + 'clips_1114.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
io.open(D + 'clips_1114.done', 'w').write('done')
