# -*- coding: utf-8 -*-
import io, os, subprocess
os.chdir('C:/Users/user/oshinavi')
msg = ('11/22 夕方（commit だけ・遅れた朝の分）：期限切れの削除 568件＝check_expired の候補 978 と独立再導出（削除は誤りという前提）568 が一致した分だけ・割れた 410 は残す（長期公演の語・年があいまい・締切不明 ほか）・logs/removed_2026-11-22.md・bak index.html.bak_1122_del\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open('tmp/x1122/msg_del22.txt', 'w', encoding='utf-8').write(msg)
out = io.open('tmp/x1122/commit_del22.txt', 'w', encoding='utf-8')
LK = 'tmp/x1112/index.lock'
import time
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'commit_del22'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    for a in (['git', 'add', 'index.html', 'logs/removed_2026-11-22.md', 'tmp/x1122'], ['git', 'commit', '-F', 'tmp/x1122/msg_del22.txt'], ['git', 'log', '--oneline', '-1']):
        r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
        out.write('%s rc=%d %s %s\n' % (a[1], r.returncode, r.stdout[-200:], r.stderr[-200:]))
finally:
    os.remove(LK)
