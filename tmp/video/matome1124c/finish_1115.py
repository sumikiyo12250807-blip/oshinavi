# -*- coding: utf-8 -*-
# par_full_1115.py の後半（作っていた係が止まったので親が続ける）：raw1・raw2 の長さを確かめる → つなぐ → 曲を重ねる → out_full / out_x → final_1115.py（点検・Downloads へ）
import io, json, os, re, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'tmp/video/matome1124c/'
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8'))
DUR = S['dur']
log = open(D + 'finish_1115.txt', 'w', encoding='utf-8')
def vlen(p):
    q = subprocess.run([ff, '-v', 'quiet', '-stats', '-i', p, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True, errors='replace').stderr
    t = re.findall(r'time=(\d+):(\d+):([\d.]+)', q)
    h, m, s = t[-1]
    return int(h) * 3600 + int(m) * 60 + float(s)
l1, l2 = vlen(D + 'raw1.mp4'), vlen(D + 'raw2.mp4')
log.write('raw1 %.2f秒（予定 52.26）raw2 %.2f秒（予定 %.2f）\n' % (l1, l2, DUR - 52.259)); log.flush()
if abs(l1 - 52.259) > 0.3 or abs(l2 - (DUR - 52.259)) > 0.3:
    log.write('長さが合わない＝途中で止まった書き出し。つながない\n'); log.close(); sys.exit(1)
io.open(D + 'concat.txt', 'w', encoding='utf-8').write("file 'raw1.mp4'\nfile 'raw2.mp4'\n")
subprocess.run([ff, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', D + 'concat.txt', '-an', '-c:v', 'copy', D + 'joined.mp4'], check=True)
full = D + 'out_full.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'joined.mp4', '-i', S['song'], '-map', '0:v', '-map', '1:a',
                    '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR,
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', full],
                   capture_output=True, text=True, errors='replace')
log.write('out_full rc %d %.2fMB\n' % (r.returncode, os.path.getsize(full) / 1048576 if os.path.exists(full) else -1)); log.flush()
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', full, '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB\n' % (r.returncode, os.path.getsize(out) / 1048576 if os.path.exists(out) else -1)); log.flush()
r = subprocess.run([sys.executable, D + 'final_1115.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('final rc %d %s\n' % (r.returncode, r.stderr[-400:]))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
