# -*- coding: utf-8 -*-
import io, os, subprocess
os.chdir('C:/Users/user/oshinavi')
msg = ('11/22 夜（commit だけ）：X の独立FCで見つけた登録の崩れ＝54916 神田伯山の出演者の欄の切れ端・37656 南佳孝の出演者と公演名の入れ替わり／11/26 演歌と舞台の動画（ミュージカル調の姐さん 3コマ・絵コンテ＋試し2本）\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open('tmp/x1122/msg_fix22.txt', 'w', encoding='utf-8').write(msg)
out = io.open('tmp/x1122/commit_fix22.txt', 'w', encoding='utf-8')
for a in (['git', 'add', 'index.html', 'plan.md', 'tmp/x1122', 'tmp/video/bg_used.md', 'tmp/video/matome1126m/set_1126m.py', 'tmp/video/matome1126m/move_cut1126.py', 'tmp/video/matome1126m/unchecker.py', 'tmp/video/matome1126m/mk_board_1126m.py', 'tmp/video/matome1126m/prep1126m.py'], ['git', 'commit', '-F', 'tmp/x1122/msg_fix22.txt'], ['git', 'log', '--oneline', '-1']):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('%s rc=%d %s %s\n' % (a[1], r.returncode, r.stdout[-200:], r.stderr[-200:]))
