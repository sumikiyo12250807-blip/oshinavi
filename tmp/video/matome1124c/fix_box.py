# -*- coding: utf-8 -*-
# 11/18 タップの枠がバッジより約 85px 下にずれた（撮った画面の 54 秒のコマで目で測った：バッジ 915〜1145・枠 1000〜1230）→ 枠を 85px 上げる → 設計図・静止画・締めの試し動画
import io, json, os, shutil, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
j = json.load(io.open(D + 'cards/screen_badge.json'))
j['boxes'] = [[x0, y0 - 85, x1, y1 - 85] for x0, y0, x1, y1 in j['boxes']]
json.dump(j, io.open(D + 'cards/screen_badge.json', 'w'))
log = ['boxes %s' % j['boxes']]
for a in (['make_spec.py'], ['render.py', '--frames', '54.0,58.0'], ['contact17.py'], ['render.py', '--clip', '50.0,76.1']):
    r = subprocess.run([sys.executable, D + a[0]] + a[1:], capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.append('%s rc=%d' % (' '.join(a), r.returncode))
shutil.copyfile(D + 'clip.mp4', D + 'clip_b.mp4')
io.open(D + 'fix_box.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
