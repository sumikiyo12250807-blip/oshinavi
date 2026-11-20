# -*- coding: utf-8 -*-
# 11/7 訂正（すちこ「最後はお辞儀してる子だけ揺らさないで」）＝締めの k5（後奏も）も止める・後奏のほかの8人はそのまま動かす
#   頭（seg_head.mp4＝k4 を止めた版・still1107 で作った）＋まん中（20:53 版 raw_full の 213〜3317 コマ）＋締め（110.6 秒〜を作り直し＝876 コマ）をつなぐ
import io, os, re, shutil, subprocess, sys, datetime, json
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
log = open(D + 'still1107b.txt', 'w', encoding='utf-8')
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
a = "    if name == 'k4':   # 11/7 すちこ「お辞儀してる時は揺らさないで」＝始まりのお辞儀の子だけ動かさない\n"
assert a in s
s = s.replace(a, "    if name in ('k4', 'k5'):   # 11/7 すちこ「お辞儀してる時は揺らさないで」＝始まり k4・締め k5（後奏の列の子は今までどおり）\n")
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
log.write('start %s\n' % datetime.datetime.now().strftime('%H:%M:%S')); log.flush()
p = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '110.6,139.8', '--out', D + 'seg_tail.mp4'], capture_output=True, env=env)
log.write('seg_tail rc %s %s %s\n' % (p.returncode, datetime.datetime.now().strftime('%H:%M:%S'), p.stderr.decode('utf-8', 'replace')[-600:])); log.flush()
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
S = json.load(io.open(D + 'stage_1118.json', encoding='utf-8'))
DUR = S['dur']
fc = ('[0:v]setpts=PTS-STARTPTS[a];[1:v]trim=start_frame=213:end_frame=3318,setpts=PTS-STARTPTS[b];[2:v]setpts=PTS-STARTPTS[c];'
      '[a][b][c]concat=n=3:v=1:a=0,fade=t=out:st=%.2f:d=1.5[v]' % (DUR - 1.5))
vk = int((8.5 * 8 * 1024) / DUR) - 128
out = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'seg_head.mp4', '-i', D + 'raw_full.mp4', '-i', D + 'seg_tail.mp4', '-i', S['song'],
                    '-filter_complex', fc, '-map', '[v]', '-map', '3:a', '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR, '-r', '30',
                    '-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out], capture_output=True, text=True, errors='replace')
log.write('out_x rc %d %.2fMB %s\n' % (r.returncode, os.path.getsize(out) / 1048576, r.stderr[-400:])); log.flush()
if r.returncode == 0:
    shutil.copyfile(out, 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4')
    subprocess.run([ff, '-y', '-v', 'error', '-i', out, '-t', '5', '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/head5.mp4'])
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (DUR - 10), '-i', out, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-movflags', '+faststart', D + 'art2/tail10.mp4'])
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '0.5', '-i', out, '-frames:v', '1', '-q:v', '3', D + 'art2/f_head.jpg'])
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (DUR - 3.0), '-i', out, '-frames:v', '1', '-q:v', '3', D + 'art2/f_tail.jpg'])
    for k in range(6):
        subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (1.0 + 0.15 * k), '-i', out, '-frames:v', '1', '-q:v', '4', D + 'frames/still_%d.jpg' % k])
        subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % (130.0 + 0.15 * k), '-i', out, '-frames:v', '1', '-q:v', '4', D + 'frames/stillt_%d.jpg' % k])
    rr = subprocess.run([ff, '-i', 'C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4'], capture_output=True, text=True, errors='replace').stderr
    log.write('downloads %s %.2fMB\n' % (' '.join(re.findall(r'Duration: [\d:.]+|\d+x\d+|\d+ fps', rr)), os.path.getsize('C:/Users/user/Downloads/oshinavi_1107_owarai_matome.mp4') / 1048576))
log.write('done %s\n' % datetime.datetime.now().strftime('%H:%M:%S'))
log.close()
open(D + 'still1107b.done', 'w').close()
