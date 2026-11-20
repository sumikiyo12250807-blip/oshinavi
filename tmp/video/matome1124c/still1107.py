# -*- coding: utf-8 -*-
# 11/7 すちこ 20:5x「お辞儀してる時は揺らさないで」→「最後はいいよ」＝始まりの k4 だけ拍の沈み・傾きを止めて静かに置く
#   書き出しは k4 の出ている頭（0〜7.1 秒＝213 コマ）だけ作り直し、残り（213 コマ〜終わり）は 20:53 版の raw_full.mp4 をそのまま使ってつなぐ
#   → 曲を重ねて X 用 → Downloads を差し替え・確認ページの頭5秒
import io, os, re, shutil, subprocess, sys, datetime, json
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
log = open(D + 'still1107.txt', 'w', encoding='utf-8')
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
a = "    sink = SINK * hh * min(1.0, f)\n    ang = TILT * math.cos(math.pi * (i + p)) if tilt else 0\n"
assert a in s
if "name == 'k4'" not in s:
    s = s.replace(a, a + "    if name == 'k4':   # 11/7 すちこ「お辞儀してる時は揺らさないで」＝始まりのお辞儀の子だけ動かさない\n        sink, ang = 0.0, 0\n")
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
log.write('start %s\n' % datetime.datetime.now().strftime('%H:%M:%S')); log.flush()
p = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '0,7.1', '--out', D + 'seg_head.mp4'], capture_output=True, env=env)
log.write('seg_head rc %s %s %s\n' % (p.returncode, datetime.datetime.now().strftime('%H:%M:%S'), p.stderr.decode('utf-8', 'replace')[-600:])); log.flush()
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8'))
DUR = S['dur']
fc = ('[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=start_frame=213,setpts=PTS-STARTPTS[b];'
      '[a][b]concat=n=2:v=1:a=0,fade=t=out:st=%.2f:d=1.5[v]' % (DUR - 1.5))
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'seg_head.mp4', '-i', D + 'raw_full.mp4', '-i', S['song'],
                    '-filter_complex', fc, '-map', '[v]', '-map', '2:a', '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR, '-r', '30',
                    '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB %s\n' % (r.returncode, os.path.getsize(out) / 1048576, r.stderr[-400:])); log.flush()
if r.returncode == 0:
    shutil.copyfile(out, 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4')
    subprocess.run([ff, '-y', '-v', 'error', '-i', out, '-t', '5', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/head5.mp4'])
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (DUR - 10), '-i', out, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/tail10.mp4'])
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '0.5', '-i', out, '-frames:v', '1', '-q:v', '3', D + 'art2/f_head.jpg'])
    # 揺れが止まったかの確かめ：頭の 1.0〜1.9 秒を 0.15 秒おきに6コマ
    for k in range(6):
        subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (1.0 + 0.15 * k), '-i', out, '-frames:v', '1', '-q:v', '4', D + 'frames/still_%d.jpg' % k])
    rr = subprocess.run([ff, '-i', 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4'], capture_output=True, text=True, errors='replace').stderr
    log.write('downloads %s %.2fMB\n' % (' '.join(re.findall(r'Duration: [\d:.]+|\d+x\d+|\d+ fps', rr)), os.path.getsize('C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4') / 1048576))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
open(D + 'still1107.done', 'w').close()
