# -*- coding: utf-8 -*-
# 今夜つける2本の動画を check_x_video で確かめる（mat01 スポーツ・おでかけ・舞台＝クラシックとおでかけ／mat03 音楽＝ライブ・どちらも 1124 の動画）
import subprocess, io, os
D = os.path.expanduser('~') + '/Downloads/'
P = 'C:/Users/user/oshinavi/tmp/x1123/x/post/'
out = io.open('C:/Users/user/oshinavi/tmp/x1123/x/check_vid1124.txt', 'w', encoding='utf-8')
for p, f in (('mat01', 'oshinavi_1124_classic_matome_x.mp4'), ('mat03', 'oshinavi_1124_live_matome_x.mp4')):
    r = subprocess.run(['python', 'C:/Users/user/oshinavi/tools/check_x_video.py', P + p + '.txt', D + f], capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('%s %s rc=%d\n%s\n%s\n' % (p, f, r.returncode, r.stdout[-800:], r.stderr[-400:]))
