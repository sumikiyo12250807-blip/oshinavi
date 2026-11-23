# -*- coding: utf-8 -*-
# 11/23 抜き打ち：TIGET（37549・49411・29800）を番人→heal_tiget（鍵を取って）→番人／FANY 売り切れ（20204・22817）
import io, os, subprocess, sys, time
R = 'C:/Users/user/oshinavi/'
os.chdir(R)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(R + 'tmp/x1123/spot/fix_tf.txt', 'w', encoding='utf-8')
def run(args):
    p = subprocess.run([sys.executable] + args, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('$ %s\nexit %d\n%s\n%s\n' % (' '.join(args), p.returncode, p.stdout[-3000:], p.stderr[-1500:]))
    out.flush()
    return p.returncode
def report(path):
    out.write('--- %s ---\n%s\n' % (path, io.open(R + path, encoding='utf-8').read()[-3000:]))
T = '37549,49411,29800'
run(['tools/gate_tiget_slots.py', '--ids', T]); report('tmp/gate_tiget_report.txt')
run(['tools/heal_tiget.py', '--ids', T]); report('tmp/heal_tiget_report.txt')
LOCK = R + 'tmp/x1112/index.lock'
fd = None
for i in range(600):
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); break
    except FileExistsError:
        time.sleep(1)
assert fd is not None, 'lock'
try:
    run(['tools/heal_tiget.py', '--ids', T, '--apply']); report('tmp/heal_tiget_report.txt')
finally:
    os.close(fd); os.remove(LOCK)
run(['tools/gate_tiget_slots.py', '--ids', T]); report('tmp/gate_tiget_report.txt')
run(['tools/fany_mark_soldout.py', '--ids', '20204,22817,23411', '--apply']); report('tmp/fany_soldout_report.txt')
