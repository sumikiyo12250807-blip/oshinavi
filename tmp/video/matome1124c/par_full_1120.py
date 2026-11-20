# -*- coding: utf-8 -*-
# 11/6 お笑いまとめ：全部の書き出しを2本同時に（前半・後半を別のプロセスで）→ 映像をつなぎ、曲を1本まるごと重ねて X 用（8.5MB 狙い）に
#   🚨 spec は先に1回作っておく（render.py が make_spec を呼ぶ＝2本同時だと _v.json の読み書きがぶつかる）→ 2本目は 30 秒ずらして起こす
#   使い方: python tmp/video/matome1124c/par_full.py   → out_x.mp4・par_full.txt
import io, json, os, re, subprocess, sys, datetime, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
src = io.open(D + 'render.py', encoding='utf-8').read()
a = "D + 'clip.mp4'"
assert src.count(a) == 2, src.count(a)
src = src.replace(a, "OUTP")
src = src.replace("FR = None\n", "FR = None\nOUTP = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else D + 'clip.mp4'\n", 1)
io.open(D + 'render_p.py', 'w', encoding='utf-8').write(src)
subprocess.run([sys.executable, D + 'make_spec.py'], check=True, capture_output=True)
S = json.load(io.open(D + 'jpop_1120.json', encoding='utf-8'))
DUR = S['dur']
CUT = 52.76   # 11/20 うさぎ t4 に着替える拍の頭
_OLD = 40.591   # 11/18 和の扇に着替える拍の頭                                   # 11/13 着替え（r5→n3）の拍の頭＝まん中あたり
edges = [0.0, CUT, DUR]
log = open(D + 'par_full.txt', 'w', encoding='utf-8')
log.write('start %s edges %s\n' % (datetime.datetime.now().strftime('%H:%M:%S'), edges)); log.flush()
ps = []
for k in range(2):
    ps.append(subprocess.Popen([sys.executable, D + 'render_p.py', '--clip', '%.3f,%.3f' % (edges[k], edges[k + 1]), '--out', D + 'raw%d.mp4' % (k + 1)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE))
    ps[-1].wait()   # 1本ずつ（重い道具は2本まで）
for k, p in enumerate(ps):
    o, e = p.communicate()
    log.write('raw%d rc %s %s %s\n' % (k + 1, p.returncode, datetime.datetime.now().strftime('%H:%M:%S'), e.decode('utf-8', 'replace')[-500:])); log.flush()
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
io.open(D + 'concat.txt', 'w', encoding='utf-8').write("file 'raw1.mp4'\nfile 'raw2.mp4'\n")
subprocess.run([ff, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', D + 'concat.txt', '-an', '-c:v', 'copy', D + 'joined.mp4'], check=True)
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'joined.mp4', '-i', S['song'], '-map', '0:v', '-map', '1:a',
                    '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR,
                    '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB %s\n' % (r.returncode, os.path.getsize(out) / 1048576 if os.path.exists(out) else -1, r.stderr[-300:]))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
