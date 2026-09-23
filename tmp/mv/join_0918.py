# -*- coding: utf-8 -*-
"""H3の10秒×2本をつないで20秒の1本にする（2026-09-18）。

音は各クリップに付いてきたものを捨て、**元のmp3の29.8秒から20秒**を1本で載せる
（つなぎ目で音が途切れないように・H3が音を作り直している可能性を避ける）。
映像は同じ規格（1440x2560・24fps・h264）なので concat デマクサで無劣化に繋ぐ。

  python tmp/mv/join_0918.py
"""
import os
import subprocess

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
MP3 = r'C:\Users\user\Downloads\おしなび特典.mp3'
OUT = 'tmp/mv/oshinavi_h3_20s.mp4'
LIST = 'tmp/mv/join_list.txt'

with open(LIST, 'w', encoding='utf-8') as f:
    for p in ('h3_1.mp4', 'h3_2.mp4'):
        f.write("file '%s'\n" % os.path.abspath(os.path.join('tmp/mv', p)).replace('\\', '/'))

silent = 'tmp/mv/_joined_silent.mp4'
r = subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                    '-i', LIST, '-an', '-c:v', 'copy', silent], capture_output=True)
if r.returncode != 0:
    raise SystemExit('つなぎで落ちた:\n' + r.stderr.decode('utf-8', 'replace')[-800:])

r = subprocess.run([FF, '-y', '-hide_banner', '-loglevel', 'error',
                    '-i', silent, '-ss', '29.8', '-t', '20', '-i', MP3,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', OUT], capture_output=True)
if r.returncode != 0:
    raise SystemExit('音を付けるところで落ちた:\n' + r.stderr.decode('utf-8', 'replace')[-800:])
os.remove(silent)
print('できた: %s （%.1fMB）' % (OUT, os.path.getsize(OUT) / 1e6))
