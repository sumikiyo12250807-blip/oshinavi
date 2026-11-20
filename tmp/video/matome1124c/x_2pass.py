# -*- coding: utf-8 -*-
# X 用の作り直し：8.5MB までのまま、720×1280 に下げて2パス（-pass 1/2）で書き出す＝44.6 秒の着替えの四角いにじみを消す
#   元＝つないだ映像 joined.mp4 ＋ 曲。終わり1.5秒のフェードは今までどおり
#   → Downloads/oshinavi_1119_classic_matome_x.mp4 を差し替え → 長さ・音・0秒・44〜46秒・終わり2秒前を確かめる
import io, os, re, shutil, subprocess
from PIL import Image
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
XX = 'C:/Users/user/Downloads/oshinavi_1119_classic_matome_x.mp4'
DUR = 96.02
ab = 128
vk = int((8.3 * 8 * 1024) / DUR) - ab        # 少し余裕を見て 8.3MB 狙い
os.chdir(D)
common = ['-vf', 'scale=720:1280:flags=lanczos,fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-c:v', 'libx264', '-b:v', '%dk' % vk, '-preset', 'slow', '-pix_fmt', 'yuv420p']
r1 = subprocess.run([ff, '-y', '-v', 'error', '-i', 'joined.mp4', '-t', '%.2f' % DUR] + common + ['-pass', '1', '-passlogfile', 'x2p', '-an', '-f', 'mp4', 'NUL'],
                    capture_output=True, text=True, errors='replace')
r2 = subprocess.run([ff, '-y', '-v', 'error', '-i', 'joined.mp4', '-i', 'song.mp3', '-map', '0:v', '-map', '1:a', '-t', '%.2f' % DUR] + common +
                    ['-pass', '2', '-passlogfile', 'x2p', '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-c:a', 'aac', '-b:a', '%dk' % ab, '-movflags', '+faststart', 'out_x2.mp4'],
                    capture_output=True, text=True, errors='replace')
out = ['pass1 rc %d %s' % (r1.returncode, r1.stderr[-200:]), 'pass2 rc %d %s' % (r2.returncode, r2.stderr[-200:]), 'v %dk' % vk]
shutil.copyfile('out_x2.mp4', XX)
e = subprocess.run([ff, '-i', XX], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
ln = []
for sel in ('v:0', 'a:0'):
    e2 = subprocess.run([ff, '-v', 'info', '-i', XX, '-map', '0:' + sel, '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    t = re.findall(r'time=(\d+):(\d+):([\d.]+)', e2)
    ln.append('%s %.2f秒' % ('映像' if sel[0] == 'v' else '音', int(t[-1][1]) * 60 + float(t[-1][2])) if t else '?')
out.append('X %.2fMB %s %s' % (os.path.getsize(XX) / 1048576, ' '.join(re.findall(r'Duration: [\d:.]+|\d{3,}x\d{3,}', e)), ' '.join(ln)))
shots = []
for t in (0.0, 44.0, 44.4, 44.6, 44.8, 45.0, 45.5, 46.0, 94.0):
    p = 'x2_%05.1f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-i', XX, '-ss', str(t), '-frames:v', '1', p])
    shots.append(Image.open(p).convert('RGB').resize((360, 640)))
o = Image.new('RGB', (360 * 5, 640 * 2))
for i, s in enumerate(shots):
    o.paste(s, ((i % 5) * 360, (i // 5) * 640))
o.save('x2_peek.png')
io.open('x_2pass.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
