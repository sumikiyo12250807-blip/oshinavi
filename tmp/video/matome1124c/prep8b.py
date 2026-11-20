# -*- coding: utf-8 -*-
# 11/4：絵コンテの秒を今日の曲に（9着＋タップ＋締め）→ board.py
import io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
s = io.open(D + 'board.py', encoding='utf-8').read()
a = 'TS = [3.8, 11.4, 19.5, 26.3, 33.8, 41.8, 48.6, 56.0, 63.4, 70.8, 78.2, 88.4, 103.1]'
assert a in s
s = s.replace(a, 'TS = [3.0, 8.0, 12.5, 17.5, 22.5, 28.0, 32.5, 37.0, 40.5, 44.0, 48.0, 53.0, 60.0]')
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, D + 'board.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.returncode, r.stderr[-1500:])
print(io.open(D + 'board.txt', encoding='utf-8').read())
