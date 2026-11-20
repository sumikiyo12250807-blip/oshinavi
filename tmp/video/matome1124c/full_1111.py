# -*- coding: utf-8 -*-
# 11/11 お笑いまとめ 全編（すちこ「OK　これで動画作って」）：裏で livePocket が回っている＝重い道具は同時2本まで → 書き出しは1本（0〜終わり）
#   render.py → render_p.py（--out 付き）→ raw_full.mp4 → 曲を1本まるごと重ねて X 用（8.5MB 狙い）→ Downloads/oshinavi_1111_owarai_matome.mp4
import io, json, os, shutil, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
src = io.open(D + 'render.py', encoding='utf-8').read()
a = "D + 'clip.mp4'"
assert src.count(a) == 2, src.count(a)
src = src.replace(a, "OUTP")
src = src.replace("FR = None\n", "FR = None\nOUTP = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else D + 'clip.mp4'\n", 1)
io.open(D + 'render_p.py', 'w', encoding='utf-8').write(src)
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8'))
DUR = S['dur']
log = open(D + 'full_1111.txt', 'w', encoding='utf-8')
log.write('start %s dur %.2f\n' % (datetime.datetime.now().strftime('%H:%M:%S'), DUR)); log.flush()
r = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '0.0,%.3f' % DUR, '--out', D + 'raw_full.mp4'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('raw rc %s %s %s\n' % (r.returncode, datetime.datetime.now().strftime('%H:%M:%S'), r.stderr[-500:])); log.flush()
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'raw_full.mp4', '-i', S['song'], '-map', '0:v', '-map', '1:a',
                    '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR,
                    '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB %s\n' % (r.returncode, os.path.getsize(out) / 1048576 if os.path.exists(out) else -1, r.stderr[-300:]))
if r.returncode == 0:
    shutil.copyfile(out, 'C:/Users/user/Downloads/oshinavi_1111_owarai_matome.mp4')
    log.write('copied to Downloads\n')
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
open(D + 'full_1111.done', 'w').close()
