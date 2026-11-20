# -*- coding: utf-8 -*-
# 11/7 お笑いまとめ 全編の書き出し（1本ずつ＝裏で e+ の照合が走っているので render は1プロセス）
#   → out_x.mp4（8.5MB 狙い）→ Downloads/oshinavi_1107_owarai_matome.mp4 ／確認用に頭5秒・終わり10秒を art/ に切り出す
import io, json, os, shutil, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
import numpy as np
from PIL import Image
# k5 のいちばん上に残った k2 のぞうりの底のかけら（暗い色・上 8 行）を消す
im = Image.open(D + 'poses/k5.png').convert('RGBA')
a = np.asarray(im).copy()
top = a[:8]
dark = top[:, :, :3].max(axis=2) < 90
top[:, :, 3][dark] = 0
a[:8] = top
Image.fromarray(a).save(D + 'poses/k5.png')
log = open(D + 'full1107.txt', 'w', encoding='utf-8')
src = io.open(D + 'render.py', encoding='utf-8').read()
src = src.replace("D + 'clip.mp4'", "OUTP")
src = src.replace("FR = None\n", "FR = None\nOUTP = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else D + 'clip.mp4'\n", 1)
io.open(D + 'render_p.py', 'w', encoding='utf-8').write(src)
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8')) if os.path.exists(D + 'stage_1118.json') else None
subprocess.run([sys.executable, D + 'make_spec.py'], check=True, capture_output=True)
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8'))
DUR = S['dur']
log.write('start %s dur %s\n' % (datetime.datetime.now().strftime('%H:%M:%S'), DUR)); log.flush()
p = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '0,%.3f' % DUR, '--out', D + 'raw_full.mp4'], capture_output=True)
log.write('raw rc %s %s %s\n' % (p.returncode, datetime.datetime.now().strftime('%H:%M:%S'), p.stderr.decode('utf-8', 'replace')[-500:])); log.flush()
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'raw_full.mp4', '-i', S['song'], '-map', '0:v', '-map', '1:a',
                    '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR,
                    '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB %s\n' % (r.returncode, os.path.getsize(out) / 1048576 if os.path.exists(out) else -1, r.stderr[-300:])); log.flush()
shutil.copyfile(out, 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4')
os.makedirs(D + 'art2', exist_ok=True)
subprocess.run([ff, '-y', '-v', 'error', '-i', out, '-t', '5', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/head5.mp4'])
subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (DUR - 10), '-i', out, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/tail10.mp4'])
for t, n in ((0.5, 'f_head.jpg'), (DUR - 1.0, 'f_tail.jpg')):
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', out, '-frames:v', '1', '-q:v', '3', D + 'art2/' + n])
rr = subprocess.run([ff, '-i', 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4'], capture_output=True, text=True, errors='replace').stderr
import re
log.write('downloads %s %.2fMB\n' % (' '.join(re.findall(r'Duration: [\d:.]+|\d+x\d+|Audio: \w+', rr)), os.path.getsize('C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4') / 1048576))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
open(D + 'full1107.done', 'w').close()
