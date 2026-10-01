# -*- coding: utf-8 -*-
# clip2_x と clip3 の中身（音のあり・なし、長さ、大きさ）を比べる
import subprocess, imageio_ffmpeg, re
ff = imageio_ffmpeg.get_ffmpeg_exe()
for f in ('clip2_x.mp4', 'clip2.mp4', 'clip3.mp4', 'seg3.mp3'):
    p = subprocess.run([ff, '-i', 'C:/Users/user/oshinavi/tmp/video/mamma/' + f], capture_output=True)
    e = p.stderr.decode('utf-8', 'replace')
    print(f, re.findall(r'Duration: [\d:.]+', e), re.findall(r'Stream #\S+: (\w+): (\w+)[^\n]*?(\d{3,4}x\d{3,4})?', e))
