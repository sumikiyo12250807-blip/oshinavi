# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ（普段着の清楚な姐さん・同じ服で動く）：すちこ「今日はこれでもういいけど」→ 全編の書き出し（final_1123m.py の形）
#   🚨重い書き出しは同時1本＝ライブ（tmp/video/matome1124l）の final の done ができてから始める
#   render.py を render_p.py（--out 付き）に写す → 前半 0〜46.643（藤色の…白いシャツとデニム t7 に着替える拍の頭）・後半〜終わり
#   → つないで曲を1本まるごと重ねる → TikTok 用（crf 18）と X 用（_x・8.5MB 狙い＝10MB 未満）
#   → Downloads/oshinavi_1124_classic_matome.mp4・_x.mp4 → 長さ・音と映像・コマ（0秒・途中・つなぎ目・終わり2秒前）
import glob, io, json, os, re, shutil, subprocess, sys, datetime, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
log = io.open(D + 'final_1124c.txt', 'w', encoding='utf-8')
def W(m):
    log.write(datetime.datetime.now().strftime('%H:%M:%S ') + m + '\n'); log.flush()
W('ライブの書き出しを待つ')
while not glob.glob('tmp/video/matome1124l/final*.done'):
    time.sleep(30)
W('ライブ終わり %s' % glob.glob('tmp/video/matome1124l/final*.done'))
src = io.open(D + 'render.py', encoding='utf-8').read()
a = "D + 'clip.mp4'"
assert src.count(a) == 2, src.count(a)
src = src.replace(a, "OUTP")
src = src.replace("FR = None\n", "FR = None\nOUTP = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else D + 'clip.mp4'\n", 1)
io.open(D + 'render_p.py', 'w', encoding='utf-8').write(src)
subprocess.run([sys.executable, D + 'make_spec.py'], check=True, capture_output=True)
S = json.load(io.open(D + 'music_1123.json', encoding='utf-8'))
DUR = S['dur']
CUT = 46.643
edges = [0.0, CUT, DUR]
W('書き出し始め edges %s' % edges)
for k in range(2):
    r = subprocess.run([sys.executable, D + 'render_p.py', '--clip', '%.3f,%.3f' % (edges[k], edges[k + 1]), '--out', D + 'raw%d.mp4' % (k + 1)],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    W('raw%d rc %d %s' % (k + 1, r.returncode, (r.stdout + r.stderr).strip()[-200:]))
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
io.open(D + 'concat.txt', 'w', encoding='utf-8').write("file 'raw1.mp4'\nfile 'raw2.mp4'\n")
subprocess.run([ff, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', D + 'concat.txt', '-an', '-c:v', 'copy', D + 'joined.mp4'], check=True)
common = ['-map', '0:v', '-map', '1:a', '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR]
big = D + 'out.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'joined.mp4', '-i', S['song']] + common +
                   ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', big],
                   capture_output=True, text=True, errors='replace')
W('大きい版 rc %d %s' % (r.returncode, r.stderr[-300:]))
vk = int((8.5 * 8 * 1024) / DUR) - 128
xo = D + 'out_x.mp4'
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'joined.mp4', '-i', S['song']] + common +
                   ['-c:v', 'libx264', '-b:v', '%dk' % vk, '-maxrate', '%dk' % vk, '-bufsize', '%dk' % (2 * vk), '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', xo], capture_output=True, text=True, errors='replace')
W('X 版 rc %d %s' % (r.returncode, r.stderr[-300:]))
DL = 'C:/Users/user/Downloads/oshinavi_1124_classic_matome.mp4'
for s_, dl in ((big, DL), (xo, 'C:/Users/user/Downloads/oshinavi_1124_classic_matome_x.mp4')):
    shutil.copyfile(s_, dl)
    e = subprocess.run([ff, '-i', dl], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    W('%s %s %.2fMB' % (os.path.basename(dl), ' '.join(re.findall(r'Duration: [\d:.]+|\d{3,4}x\d{3,4}', e)), os.path.getsize(dl) / 1048576))
    for sel in ('v:0', 'a:0'):
        e2 = subprocess.run([ff, '-v', 'info', '-i', dl, '-map', '0:' + sel, '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
        t = re.findall(r'time=(\d+):(\d+):([\d.]+)', e2)
        W('  %s の長さ %s' % ('映像' if sel[0] == 'v' else '音', '%.2f 秒' % (int(t[-1][1]) * 60 + float(t[-1][2])) if t else '?'))
for nm, ss in (('final_000', None), ('final_020', 20.5), ('final_cut', CUT + 0.2), ('final_058', 58.0), ('final_075', 75.0)):
    subprocess.run([ff, '-y', '-v', 'error'] + (['-ss', '%.2f' % ss] if ss is not None else []) + ['-i', DL, '-frames:v', '1', D + nm + '.png'])
subprocess.run([ff, '-y', '-v', 'error', '-sseof', '-2', '-i', DL, '-frames:v', '1', D + 'final_end.png'])
from PIL import Image
fs = ['final_000', 'final_020', 'final_cut', 'final_058', 'final_075', 'final_end']
ims = [Image.open(D + f + '.png').convert('RGB').resize((360, 640)) for f in fs]
row = Image.new('RGB', (360 * 6 + 50, 640), (20, 14, 30))
for i, im in enumerate(ims):
    row.paste(im, (i * 370, 0))
row.save(D + 'final_look.png')
W('コマ final_look.png（0秒・20.5秒・つなぎ目・58秒・75秒・終わり2秒前）')
io.open(D + 'final_1124c.done', 'w').write('done')
log.close()
