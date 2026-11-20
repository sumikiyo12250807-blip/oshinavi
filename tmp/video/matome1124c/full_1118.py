# -*- coding: utf-8 -*-
# 11/18 舞台・トークショー：すちこ OK（絵コンテ）→ 全編の書き出し（前半・後半を2本同時）
#   重い道具は同時2本まで＝主役の下ごしらえ（prep16a：文字起こし）が終わるのを待ってから始める
#   切る所は 40.591 秒（ほかにも＝和の扇に着替える拍の頭・まん中あたり）
import io, os, time, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
P = 'tmp/video/shuyaku1116/prep16a.txt'
for _ in range(240):
    if os.path.exists(P) and 'transcribe2.py rc' in io.open(P, encoding='utf-8', errors='replace').read():
        break
    time.sleep(15)
s = io.open(D + 'par_full.py', encoding='utf-8').read()
a = 'CUT = 51.542'
assert a in s
io.open(D + 'par_full.py', 'w', encoding='utf-8').write(s.replace(a, 'CUT = 40.591   # 11/18 和の扇に着替える拍の頭'))
r = subprocess.run([sys.executable, D + 'run_full.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(D + 'full_1118.txt', 'w', encoding='utf-8').write('rc %d\n%s\n%s\n' % (r.returncode, r.stdout[-1500:], r.stderr[-1500:]))
