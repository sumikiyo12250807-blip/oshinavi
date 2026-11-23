# -*- coding: utf-8 -*-
# 11/23 昼：鍵の中で heal_stale_deadlines --apply → check_order ／ そのあと抜き打ちのぴあ・e+ 分（refetch_artist・reconcile_pia 40637）
import io, os, subprocess, sys, time
R = 'C:/Users/user/oshinavi/'
os.chdir(R)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(R + 'tmp/x1123/spot/noon_apply.txt', 'w', encoding='utf-8')
def run(args):
    p = subprocess.run(args, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('$ %s\nexit %d\n%s\n%s\n' % (' '.join(args), p.returncode, p.stdout[-2500:], p.stderr[-1500:]))
    out.flush()
LK = R + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'noon_apply23'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    run([sys.executable, 'tools/heal_stale_deadlines.py', '--apply'])
    run(['node', 'tools/check_order.js'])
    run([sys.executable, 'tools/refetch_artist.py', '--ids', '2908,54089,4349,40637'])
    run([sys.executable, 'tools/refetch_artist.py', '--ids', '2908,54089,4349,40637', '--apply'])
finally:
    os.remove(LK)
run([sys.executable, 'tools/reconcile_pia.py', '--ids', '40637'])
