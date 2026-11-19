# -*- coding: utf-8 -*-
# 抜き打ち 🔴 2440 RENT：ぴあの実ページで枠を取り直す（鍵の中）→ 照合し直す
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1119/spot/'
LK = 'tmp/x1112/index.lock'
out = io.open(D + 'heal_2440.txt', 'w', encoding='utf-8')
def run(a):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('=== %s rc=%d\n%s\n%s\n' % (' '.join(a), r.returncode, r.stdout[-4000:], r.stderr[-1500:])); out.flush()
    return r.stdout
ids = sys.argv[1] if len(sys.argv) > 1 else '2440'
run(['tools/heal_stale_deadlines.py', '--ids', ids, '--build'])
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'spot_heal'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    run(['tools/heal_stale_deadlines.py', '--apply', '--ids', ids])
finally:
    os.remove(LK)
run(['tools/reconcile_pia.py', '--ids', ids])
