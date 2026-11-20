# -*- coding: utf-8 -*-
# 11/3：拍をスネアに当てる（位相を5窓の中央値で追う版）→ beats_snare.txt を utf-8 で見る
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, D + 'beats_snare.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(r.returncode)
print(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
