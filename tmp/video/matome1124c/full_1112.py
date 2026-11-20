# -*- coding: utf-8 -*-
# 11/12 お笑いまとめ 全編（すちこ OK）：full_1111 の写し。書き出しは1本（0〜終わり）→ raw_full.mp4 → 曲を1本まるごと重ねて X 用（8.5MB 狙い）
#   → Downloads/oshinavi_1112_owarai_matome.mp4 ・ 最初と最後のコマ（frames/chk_*.png）と長さを full_1112.txt へ
import io, json, os, re, shutil, subprocess, sys, datetime
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
log = open(D + 'full_1112.txt', 'w', encoding='utf-8')
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
    dst = 'C:/Users/user/Downloads/oshinavi_1112_owarai_matome.mp4'
    shutil.copyfile(out, dst)
    log.write('copied %s %d bytes\n' % (dst, os.path.getsize(dst)))
    # 長さ（音・映像）
    pr = subprocess.run([ff, '-i', out, '-map', '0', '-f', 'null', '-'], capture_output=True, text=True, errors='replace').stderr
    log.write('probe ' + ' | '.join(re.findall(r'Duration: [\d:.]+|Stream #0:\d.*?(?:Video|Audio): \w+|frame=\s*\d+|time=[\d:.]+', pr)[-6:]) + '\n')
    for t in (0.1, 1.0, 3.0, DUR - 3.0, DUR - 1.0, DUR - 0.1):
        subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', out, '-frames:v', '1', '-vf', 'scale=270:480', D + 'frames/chk_%05.1f.png' % t])
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
open(D + 'full_1112.done', 'w').close()
