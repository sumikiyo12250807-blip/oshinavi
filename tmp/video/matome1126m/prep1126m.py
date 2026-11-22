# -*- coding: utf-8 -*-
# 11/26 まとめ（TikTok 先出し）の下ごしらえ（11/22 夜）
#   すちこが渡した＝曲 Downloads/おしなびどっと (40).mp3・背景 Downloads/37497_640x360.mp4
#   イメージ＝ミュージカル調（すちこ「アニーみたいな感じかな？」）
#   ①matome1125o の道具を写して置き場所を 1126m に ②曲の歌詞タグを 11/26 の歌詞2本（演歌と舞台・ポップスとロック）と比べてどちらの曲か決める
#   ③背景を縦のコマに ④テンポ ⑤文字起こし
import io, os, shutil, subprocess, sys, glob, difflib, re
S = 'C:/Users/user/oshinavi/tmp/video/matome1125o/'
D = 'C:/Users/user/oshinavi/tmp/video/matome1126m/'
DL = 'C:/Users/user/Downloads/'
X = 'C:/Users/user/oshinavi/tmp/x1122/x/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1126m.txt', 'w', encoding='utf-8')
def run(*a, tail=1500):
    r = subprocess.run([sys.executable] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, cwd=D)
    out.write('== %s rc %s\n%s\n%s\n' % (' '.join(a)[-80:], r.returncode, r.stdout[-tail:], r.stderr[-tail:])); out.flush()
    return r.returncode
for f in [x for x in glob.glob(S + '*.py') if not os.path.basename(x).startswith('prep1125o')]:
    b = os.path.basename(f)
    s = io.open(f, encoding='utf-8', errors='replace').read().replace('matome1125o', 'matome1126m')
    io.open(D + b, 'w', encoding='utf-8').write(s)
for sub in ('cards', 'poses'):
    os.makedirs(D + sub, exist_ok=True)
shutil.copyfile(DL + 'おしなびどっと (40).mp3', D + 'song.mp3')
shutil.copyfile(DL + '37497_640x360.mp4', D + 'bg_src.mp4')
shutil.copyfile(D + 'bg_src.mp4', D + 'bg.mp4')
import imageio_ffmpeg
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'song.mp3', '-f', 'ffmetadata', D + 'meta.txt'])
m = io.open(D + 'meta.txt', encoding='utf-8', errors='replace').read()
ly = m.split('lyrics-eng=', 1)[1].split('\ncomment=', 1)[0].replace('\\\n', '\n') if 'lyrics-eng=' in m else ''
io.open(D + 'lyrics_tag.txt', 'w', encoding='utf-8').write('== USLT\n' + ly + '\n')
norm = lambda t: re.sub(r'\s|\[[^\]]*\]', '', t)
best = None
for k in ('enka', 'pops'):
    mine = io.open(X + 'suno_%s_1126.txt' % k, encoding='utf-8').read()
    r = difflib.SequenceMatcher(None, norm(ly), norm(mine)).ratio() if ly else 0
    out.write('似ている度 %s %.3f\n' % (k, r))
    if best is None or r > best[1]:
        best = (k, r)
out.write('どちらの曲＝%s\n' % (best,))
shutil.copyfile(X + 'suno_%s_1126.txt' % best[0], D + 'mine.txt')
if ly:
    run(D + 'lyrics_diff.py')
r = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, errors='replace')
out.write('song ' + [l for l in r.stderr.splitlines() if 'Duration' in l][0] + '\n')
s = io.open(D + 'bg_prep.py', encoding='utf-8').read()
s = '# -*- coding: utf-8 -*-\n# 11/26 まとめ 37497（すちこが渡した・ミュージカル調）\n' + s.split('\n', 1)[1]
io.open(D + 'bg_prep.py', 'w', encoding='utf-8').write(s)
run(D + 'bg_prep.py')
subprocess.run([ff, '-y', '-v', 'error', '-ss', '2', '-i', D + 'bg.mp4', '-frames:v', '1', D + 'bg_wide.png'])
run(D + 'tempo_check.py', tail=300)
run(D + 'transcribe2.py', tail=300)
out.write('DONE\n')
out.close()
open(D + 'prep1126m.done', 'w').close()
