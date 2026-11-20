# -*- coding: utf-8 -*-
import glob, io, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
fs = sorted(glob.glob(D + '*.py')) + [D + 'final_1124c.txt', D + 'board_1124c.txt', 'tmp/video/bg_used.md']
io.open(D + 'msg_commit.txt', 'w', encoding='utf-8').write(
    '11/20（commit だけ）：11/24 クラシックとおでかけ まとめ動画（TikTok・X）を書き出した＝曲 おしなびどっと (38).mp3 1:37・背景 30729 夕焼けのビル街・'
    '普段着の清楚な姐さん9人＋同じ服で動いた絵（すちこ「清楚な感じよ」）→ Downloads/oshinavi_1124_classic_matome.mp4（61.4MB）・_x.mp4（8.1MB）／道具 tmp/video/matome1124c・背景の台帳\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg_commit.txt'] + fs, capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.returncode, r.stdout[-300:], r.stderr[-300:])
r = subprocess.run(['git', 'log', '--oneline', '-1'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(r.stdout)
