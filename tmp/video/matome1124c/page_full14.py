# -*- coding: utf-8 -*-
# 絵コンテのページに全編（小文字 oshinavi.jp 版・縮めて埋め込む）を足す → 同じ board_page.html を書き直す
import base64, io, os, subprocess
import imageio_ffmpeg
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
OUT = 'C:/Users/user/AppData/Local/Temp/claude/ac08c5b2b244d5f8/47d82dbe-348b-45b6-9b9c-e64a11b39c3d/scratchpad/owarai1114/board_page.html'
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'out.mp4', '-vf', 'scale=432:768', '-c:v', 'libx264', '-crf', '32', '-preset', 'medium',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'full_s.mp4'], check=True)
v = base64.b64encode(open(D + 'full_s.mp4', 'rb').read()).decode()
h = io.open(OUT, encoding='utf-8').read()
h = h.replace('<title>お笑い11/14 絵コンテ</title>', '<title>お笑い11/14 絵コンテ</title>', 1)
sec = ('<section><h2>全編（書き出した動画・67.6秒）</h2><figure style="max-width:420px">'
       '<video controls playsinline preload="metadata" src="data:video/mp4;base64,%s"></video>'
       '<figcaption>締めの字は小文字の「oshinavi.jp」にした（すちこ「検索するのは小文字だから」）。'
       'X 用の小さい版（7.8MB）と元の大きさの版を Downloads に置いた＝oshinavi_1114_owarai_matome_x.mp4・oshinavi_1114_owarai_matome.mp4</figcaption></figure></section>\n') % v
assert '<section><h2>流れ</h2>' in h
h = h.replace('<section><h2>流れ</h2>', sec + '<section><h2>流れ</h2>', 1)
io.open(OUT, 'w', encoding='utf-8').write(h)
print(len(h) // 1024, 'KB', os.path.getsize(D + 'full_s.mp4') // 1024, 'KB')
