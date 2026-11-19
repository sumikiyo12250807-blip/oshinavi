# -*- coding: utf-8 -*-
# 足した出演者の比べを試す：番人（読むだけ）→ heal_tiget --apply（鍵の中）→ 番人
import io, os, re, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1119/spot/'
LK = 'tmp/x1112/index.lock'
ids = '37905,45660,28257,45404,54512,17538,44918,50106'
out = io.open(D + 'tiget_try.txt', 'w', encoding='utf-8')
def gate(tag):
    r = subprocess.run([sys.executable, 'tools/gate_tiget_slots.py', '--ids', ids], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('=== 番人 %s rc=%d\n%s\n' % (tag, r.returncode, io.open('tmp/gate_tiget_report.txt', encoding='utf-8').read())); out.flush()
    return r.returncode
gate('前')
if '--apply' in sys.argv:
    bad = ','.join(sorted(set(re.findall(r'🚨 id=(\d+)', io.open('tmp/gate_tiget_report.txt', encoding='utf-8').read()))))
    if bad:
        while True:
            try:
                fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'spot_tiget'); os.close(fd); break
            except FileExistsError:
                time.sleep(10)
        try:
            r = subprocess.run([sys.executable, 'tools/heal_tiget.py', '--ids', bad, '--apply'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
            out.write('=== heal rc=%d %s\n%s\n' % (r.returncode, r.stderr[-300:], io.open('tmp/heal_tiget_report.txt', encoding='utf-8').read()))
        finally:
            os.remove(LK)
        gate('後')
