# -*- coding: utf-8 -*-
# 11/19 夜：gate_fields S3 1件（id2785 月例 三三独演の links.pia が受付と別の公演）を鍵の中で fix_links --apply → commit だけ
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1119/'
out = io.open(D + 'fix_links_night.txt', 'w', encoding='utf-8')
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_links_1119'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    r = subprocess.run([sys.executable, 'tools/fix_links.py', '--apply'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('fix_links rc=%d %s %s\n' % (r.returncode, r.stdout.strip(), r.stderr[-300:]))
    out.write(io.open('tmp/fix_links.txt', encoding='utf-8').read() + '\n')
    r = subprocess.run([sys.executable, 'tools/fix_links.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('あとで数え直し %s\n' % r.stdout.strip())
finally:
    os.remove(LK)
io.open(D + 'msg_fix_links.txt', 'w', encoding='utf-8').write(
    '11/19 夜（commit だけ）：gate_fields S3 1件＝id2785 月例 三三独演のぴあのボタンが受付と別の公演（eventCd 2533438）→ 受付と同じ 2533445 に（tools/fix_links.py --apply・鍵の中）\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg_fix_links.txt', 'index.html', D + 'fix_links_night.py', D + 'fix_links_night.txt', D + 'msg_fix_links.txt'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('commit rc=%d %s\n' % (r.returncode, r.stderr[-300:]))
out.close()
