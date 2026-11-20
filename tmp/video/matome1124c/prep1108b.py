# -*- coding: utf-8 -*-
# 11/8：拍＝スネア 131.4〜133.4BPM（tempo_check のスネア2位 132.4・1位 65.6 はその半分）・曲 62.9 秒
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
s = s.replace('END = 139.3', 'END = 62.5').replace('np.arange(137.0, 139.01, 0.02)', 'np.arange(131.4, 133.41, 0.02)')
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
s = s.replace("poses/k[1-9].png'))   # 11/7 着物の歌姫 k", "poses/[kn][1-9].png'))   # 11/8 祭りの子 k（元の向き）・n（反転）")
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'beats_snare.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
io.open(D + 'prep1108b.txt', 'w', encoding='utf-8').write('rc %s %s\n' % (r.returncode, r.stderr[-1500:]) + io.open(D + 'beats_snare.txt', encoding='utf-8').read())
