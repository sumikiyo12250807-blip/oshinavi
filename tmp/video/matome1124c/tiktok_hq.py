# -*- coding: utf-8 -*-
# X 用（8.5MB 狙い＝約 580kbps）は光の板が動く暗い背景で、着替えの瞬間に数コマ四角いにじみが出た（44.6 秒）
#   → TikTok 用は大きさの上限が無いので、つないだ映像から画質優先（crf 20）で作り直す＝Downloads/oshinavi_1119_classic_matome.mp4
#   X 用（8.2MB）は Downloads/oshinavi_1119_classic_matome_x.mp4 に置き直す。両方の長さ・音・0秒・つなぎ目・終わり2秒前を確かめる
import io, os, re, shutil, subprocess
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/'
DUR = 96.02
TK, XX = DL + 'oshinavi_1119_classic_matome.mp4', DL + 'oshinavi_1119_classic_matome_x.mp4'
shutil.copyfile(D + 'out_x.mp4', XX)
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'joined.mp4', '-i', D + 'song.mp3', '-map', '0:v', '-map', '1:a',
                    '-vf', 'fade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-af', 'afade=t=out:st=%.2f:d=1.5' % (DUR - 1.5), '-t', '%.2f' % DUR,
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', D + 'out_tk.mp4'],
                   capture_output=True, text=True, errors='replace')
shutil.copyfile(D + 'out_tk.mp4', TK)
out = ['tiktok rc %d' % r.returncode]
for nm, f in (('TikTok', TK), ('X', XX)):
    e = subprocess.run([ff, '-i', f], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    ln = []
    for sel in ('v:0', 'a:0'):
        e2 = subprocess.run([ff, '-v', 'info', '-i', f, '-map', '0:' + sel, '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
        t = re.findall(r'time=(\d+):(\d+):([\d.]+)', e2)
        ln.append('%s %.2f秒' % ('映像' if sel[0] == 'v' else '音', int(t[-1][1]) * 60 + float(t[-1][2])) if t else '?')
    out.append('%s %s %.2fMB %s %s' % (nm, os.path.basename(f), os.path.getsize(f) / 1048576, ' '.join(re.findall(r'Duration: [\d:.]+|\d{3,}x\d{3,}', e)), ' '.join(ln)))
    tag = 'tk' if nm == 'TikTok' else 'x'
    subprocess.run([ff, '-y', '-v', 'error', '-i', f, '-frames:v', '1', D + 'final_%s_000.png' % tag])
    subprocess.run([ff, '-y', '-v', 'error', '-i', f, '-ss', '44.6', '-frames:v', '1', D + 'final_%s_cut.png' % tag])
    subprocess.run([ff, '-y', '-v', 'error', '-sseof', '-2', '-i', f, '-frames:v', '1', D + 'final_%s_end.png' % tag])
io.open(D + 'tiktok_hq.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
