# -*- coding: utf-8 -*-
# 11/23 夜の鎖（1本ずつ）：night23（ぴあの見直し・夜のヒール）の .done を待つ → 夜の push → ぴあ発売前 → e+ 出演者ページ（二周目）→ 新しい売り場5つ → FANY 売り切れ全件
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1123/'
log = io.open(D + 'night_chain23.txt', 'a', encoding='utf-8')
def W(m):
    log.write(time.strftime('%H:%M:%S ') + m + '\n'); log.flush()
while not os.path.exists(D + 'night23.done'):
    time.sleep(60)
for f in ('night_1123.py', 'night_collect23.py', 'overnight_1123.py', 'night_newv23.py'):
    W(f + ' 開始')
    r = subprocess.run([sys.executable, D + f], env=env)
    W(f + ' rc=%d' % r.returncode)
    open(D + f.replace('.py', '.done'), 'w').write(str(r.returncode))
W('fany_mark_soldout 開始')
r = subprocess.run([sys.executable, 'tools/fany_mark_soldout.py', '--apply'], env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(D + 'night_fany_soldout.txt', 'w', encoding='utf-8').write(r.stdout + r.stderr)
W('fany_mark_soldout rc=%d' % r.returncode)
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg_fany23.txt', 'tmp/fany_soldout_report.txt'], env=env)
open(D + 'night_chain23.done', 'w').write('done')
W('おわり')
