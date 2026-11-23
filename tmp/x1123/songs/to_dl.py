# -*- coding: utf-8 -*-
# 14番の曲の動画（11/27 J-POP・ロック）を Downloads へ（TikTok 用＝大きい版・X 用＝_x）
import shutil, os, io
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
DL = 'C:/Users/user/Downloads/'
shutil.copyfile(D + 'out.mp4', DL + 'oshinavi_1127_jpoprock_matome.mp4')
shutil.copyfile(D + 'out_x.mp4', DL + 'oshinavi_1127_jpoprock_matome_x.mp4')
io.open(D + 'to_dl.txt', 'w', encoding='utf-8').write('\n'.join('%s %.1fMB' % (f, os.path.getsize(DL + f) / 1e6) for f in ('oshinavi_1127_jpoprock_matome.mp4', 'oshinavi_1127_jpoprock_matome_x.mp4')))
io.open('C:/Users/user/oshinavi/tmp/video/bg_used.md', 'a', encoding='utf-8').write('- 2026-11-23 96057（黒地に青と紫の光の粒）＝11/27 J-POP・ロックまとめ（14番の曲・サイバーパンクの姐さん）\n')
