# -*- coding: utf-8 -*-
# 11/4：曲 65.6 秒・tempo_check キック 107.2・スネア 106.6 → 105.5〜108.5BPM でスネアに当てる
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
for a, b in (('END = 110.0', 'END = 65.0'), ('np.arange(128.0, 131.61, 0.02)', 'np.arange(105.5, 108.51, 0.02)')):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, D + 'beats_snare.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(r.returncode, r.stderr[-1500:])
print(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
