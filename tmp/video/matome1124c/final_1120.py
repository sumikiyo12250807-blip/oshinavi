# -*- coding: utf-8 -*-
# 11/20 J-POP まとめ：すちこ「いいわね　両方とも　これでお願いします」（ゴスロリ描き直し版・背景 242696）→ 全編の書き出し
#   重い道具は同時2本まで（主役の書き出しは、これが終わるのを待つ）＝前半・後半を1本ずつ順に
#   切る所 52.76 秒（うさぎの t4 に着替える拍の頭・まん中あたり）→ つないで曲を重ねる（out_x.mp4）
#   → Downloads/oshinavi_1120_jpop_matome.mp4 → 長さ・音と映像・0秒・終わり2秒前を確かめる → final.done
import io, os, re, shutil, subprocess, sys, datetime
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
for f in ('final.done', 'final_1120.done'):
    if os.path.exists(D + f):
        os.remove(D + f)
s = io.open(D + 'par_full.py', encoding='utf-8').read()
for a, b in (("'stage_1118.json'", "'jpop_1120.json'"),
             ('CUT = 40.591', 'CUT = 52.76   # 11/20 うさぎ t4 に着替える拍の頭\n_OLD = 40.591'),
             ("    if k:\n        time.sleep(30)\n    ps.append(", "    ps.append("),
             ("                               stdout=subprocess.PIPE, stderr=subprocess.PIPE))\n",
              "                               stdout=subprocess.PIPE, stderr=subprocess.PIPE))\n    ps[-1].wait()   # 1本ずつ（重い道具は2本まで）\n")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'par_full_1120.py', 'w', encoding='utf-8').write(s)
log = io.open(D + 'final_1120.txt', 'w', encoding='utf-8')
def W(m):
    log.write(datetime.datetime.now().strftime('%H:%M:%S ') + m + '\n'); log.flush()
W('書き出し始め')
r = subprocess.run([sys.executable, D + 'par_full_1120.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
W('par_full rc %d %s' % (r.returncode, (r.stdout + r.stderr)[-800:]))
W(io.open(D + 'par_full.txt', encoding='utf-8', errors='replace').read())
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
DL = 'C:/Users/user/Downloads/oshinavi_1120_jpop_matome.mp4'
shutil.copyfile(D + 'out_x.mp4', DL)
e = subprocess.run([ff, '-i', DL], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
W('全体 ' + ' '.join(re.findall(r'Duration: [\d:.]+|Video: \w+[^,]*, [^,]*, \d+x\d+|Audio: \w+', e)) + ' %.2fMB' % (os.path.getsize(DL) / 1048576))
for sel in ('v:0', 'a:0'):
    e2 = subprocess.run([ff, '-v', 'info', '-i', DL, '-map', '0:' + sel, '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    t = re.findall(r'time=(\d+):(\d+):([\d.]+)', e2)
    W('%s の長さ %s' % ('映像' if sel[0] == 'v' else '音', '%.2f 秒' % (int(t[-1][1]) * 60 + float(t[-1][2])) if t else '?'))
subprocess.run([ff, '-y', '-v', 'error', '-i', DL, '-frames:v', '1', D + 'final_000.png'])
subprocess.run([ff, '-y', '-v', 'error', '-sseof', '-2', '-i', DL, '-frames:v', '1', D + 'final_end.png'])
subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.3f' % 52.9, '-i', DL, '-frames:v', '1', D + 'final_cut.png'])
W('コマ final_000.png（0秒）・final_end.png（終わり2秒前）・final_cut.png（つなぎ目のすぐ後）')
io.open(D + 'final_1120.done', 'w').write('done')
