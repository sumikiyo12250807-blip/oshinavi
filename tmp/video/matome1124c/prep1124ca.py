# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけのまとめ（TikTok 先出し）の下ごしらえ（11/20 夕方）
#   すちこが渡した＝曲 Downloads/おしなびどっと (38).mp3（1:37）・背景 Downloads/背景動画/30729_640x360.mp4
#   ①matome1123m の道具を写して置き場所を 1124c に ②曲の歌詞タグと渡した歌詞（suno_classic_1124）を突き合わせ
#   ③背景を縦のコマに ④テンポ ⑤文字起こし
import io, os, shutil, subprocess, sys, glob
S = 'C:/Users/user/oshinavi/tmp/video/matome1123m/'
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
DL = 'C:/Users/user/Downloads/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1124ca.txt', 'w', encoding='utf-8')
def run(*a, tail=1500):
    r = subprocess.run([sys.executable] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, cwd=D)
    out.write('== %s rc %s\n%s\n%s\n' % (' '.join(a)[-80:], r.returncode, r.stdout[-tail:], r.stderr[-tail:])); out.flush()
    return r.returncode
for f in [x for x in glob.glob(S + '*.py') if not os.path.basename(x).startswith('prep1123')]:
    b = os.path.basename(f)
    s = io.open(f, encoding='utf-8', errors='replace').read().replace('matome1123m', 'matome1124c')
    io.open(D + b, 'w', encoding='utf-8').write(s)
for sub in ('cards', 'poses'):
    os.makedirs(D + sub, exist_ok=True)
shutil.copyfile(DL + 'おしなびどっと (38).mp3', D + 'song.mp3')
shutil.copyfile(DL + '背景動画/30729_640x360.mp4', D + 'bg_src.mp4')
shutil.copyfile(D + 'bg_src.mp4', D + 'bg.mp4')
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'song.mp3', '-f', 'ffmetadata', D + 'meta.txt'])
m = io.open(D + 'meta.txt', encoding='utf-8', errors='replace').read()
ly = m.split('lyrics-eng=', 1)[1].split('\ncomment=', 1)[0].replace('\\\n', '\n') if 'lyrics-eng=' in m else ''
io.open(D + 'lyrics_tag.txt', 'w', encoding='utf-8').write('== USLT\n' + ly + '\n')
shutil.copyfile('C:/Users/user/oshinavi/tmp/x1120/x/suno_classic_1124.txt', D + 'mine.txt')
if ly:
    run(D + 'lyrics_diff.py')
r = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, errors='replace')
out.write('song ' + [l for l in r.stderr.splitlines() if 'Duration' in l][0] + '\n')
s = io.open(D + 'bg_prep.py', encoding='utf-8').read()
s = '# -*- coding: utf-8 -*-\n# 11/24 クラシックとおでかけ 30729（すちこが渡した）\n' + s.split('\n', 1)[1]
io.open(D + 'bg_prep.py', 'w', encoding='utf-8').write(s)
run(D + 'bg_prep.py')
subprocess.run([ff, '-y', '-v', 'error', '-ss', '2', '-i', D + 'bg.mp4', '-frames:v', '1', D + 'bg_wide.png'])
run(D + 'tempo_check.py', tail=300)
run(D + 'transcribe2.py', tail=300)
out.write('DONE\n')
out.close()
open(D + 'prep1124ca.done', 'w').close()
