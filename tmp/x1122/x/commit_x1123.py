# -*- coding: utf-8 -*-
import io, os, subprocess
os.chdir('C:/Users/user/oshinavi')
msg = ('11/22 夕方（commit だけ）：X 11/23 発売を1晩5本の新しい形で予約（すちこ「主役は1本でいい」「5件にしよう」＝X_SCRIPT に書いた・トレンド 大相撲冬巡業・スポーツ/おでかけ/舞台・お笑い・音楽・主役 好井まさお／独立FC 2回）・X の数字の取り直し（3か月の週ごとの表示とフォロー・_followers 11/22 92人）・その日のアラームの番人 alarm_guard.py\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open('tmp/x1122/x/msg_x1123.txt', 'w', encoding='utf-8').write(msg)
out = io.open('tmp/x1122/x/commit_x1123.txt', 'w', encoding='utf-8')
for a in (['git', 'add', 'plan.md', 'X_SCRIPT.md', 'tmp/x1122', 'tmp/x_media_log.json', '.claude/hooks/alarm_guard.py'], ['git', 'commit', '-F', 'tmp/x1122/x/msg_x1123.txt'], ['git', 'log', '--oneline', '-1']):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('%s rc=%d %s %s\n' % (a[1], r.returncode, r.stdout[-300:], r.stderr[-200:]))
