# -*- coding: utf-8 -*-
import io, os, subprocess
os.chdir('C:/Users/user/oshinavi')
msg = ('11/22 朝（commit だけ）：11/26(木)発売のまとめ歌詞2本（演歌と舞台・ポップスとロック）＝material_1126 → 登録と機械で突き合わせ 0・独立FC 0・読みの出典なし2組（ラムネ商店街・Dazzling BAD）は外した → コピーのページ・plan.md 先頭の「いまの歌詞」を差し替え\n\n'
       'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
io.open('tmp/x1122/x/msg_lyrics.txt', 'w', encoding='utf-8').write(msg)
out = io.open('tmp/x1122/x/commit_lyrics.txt', 'w', encoding='utf-8')
for a in (['git', 'add', 'plan.md', 'tmp/x1122/x'], ['git', 'commit', '-F', 'tmp/x1122/x/msg_lyrics.txt'], ['git', 'log', '--oneline', '-1'], ['git', 'log', '--oneline', 'origin/main..HEAD']):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('%s rc=%d %s %s\n' % (a[1], r.returncode, r.stdout[-500:], r.stderr[-200:]))
