# -*- coding: utf-8 -*-
# 11/12：絵コンテ（場面ごと・曲の全部）→ 試し動画1本（11.5〜19.0 秒＝最初の名前の行・着替え2回）→ 小さく
import io, os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1112c.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    out.flush()
    return r.returncode


if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
n = len(P) - 1
TS = [1.0, 6.0]
for i in range(n):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < n else tap)) / 2
    TS.append(round(m, 1))
bt = S['beat']
TS += [round(P[2][0] + 0.3, 1), round(tap + 2.0, 1), round(tap + 6.0, 1), round(url + 1.0, 1), round(url + bt * 12 + 1.0, 1),
       round(url + bt * 28 + 1.0, 1), round(S['dur'] - 2.0, 1)]
TS = sorted(set(TS))
out.write('poses %s\ntap %.2f url %.2f\nTS %s\n' % ([[round(t, 2), p] for t, p in P], tap, url, TS))
bd = io.open(D + 'board.py', encoding='utf-8').read()
bd, k = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, bd, count=1)
assert k == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(bd)
run('board.py')
run('render.py', '--clip', '11.5,19.0')
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'clip.mp4', '-vf', 'scale=540:960', '-c:v', 'libx264', '-crf', '26', '-preset', 'medium',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'test_clip.mp4'], check=True)
out.write('test_clip %d KB\n' % (os.path.getsize(D + 'test_clip.mp4') // 1024))
out.close()
open(D + 'prep1112c.done', 'w').close()
