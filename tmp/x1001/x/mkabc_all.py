# 10本ぶんの予約JS（A/B/C）を作る：20:01から15分おき
import subprocess, sys
T = [(20, 1), (20, 16), (20, 31), (20, 46), (21, 1), (21, 16), (21, 31), (21, 46), (22, 1), (22, 16)]
for k, (h, m) in enumerate(T, 1):
    subprocess.run([sys.executable, 'tmp/x1001/x/mkabc.py', '%02d' % k, str(h), str(m)], check=True)
