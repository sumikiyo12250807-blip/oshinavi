# -*- coding: utf-8 -*-
# 11/19 記事3本（すちこ「OK」）を pickup/a/ に組み、台帳に登録 → pickup_list --apply（鍵の中）→ CD・宿のボタン → commit（push は夜）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1119/art19/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
A = [
 ('daibakushow', 'DAIBAKUSHOW', '12/30(水) 10:00／16:30 東京・東京ガーデンシアター', '43373'),
 ('asagaya', '阿佐ヶ谷姉妹', 'R9年 2/28(日) 14:00 静岡・グランシップ 大ホール・海', '34053'),
 ('plastictree', 'Plastic Tree', '12/27(日) 18:30 神奈川・カルッツかわさき ホール', '31191'),
]
for slug, q, shows, w in A:
    r = subprocess.run([sys.executable, 'tools/pickup_article.py', D + slug + '.md', slug, '--q', q,
                        '--shows-head', '発売になる公演', '--shows', shows, '--watch', w],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d %s %s\n' % (slug, r.returncode, r.stdout.strip(), r.stderr[-500:])); out.flush()
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1119'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    r = subprocess.run([sys.executable, 'tools/pickup_list.py', '--apply'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('pickup_list rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-2000:], r.stderr[-800:]))
finally:
    os.remove(LK)
r = subprocess.run([sys.executable, 'tools/pickup_cd_btn.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('pickup_cd_btn rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-1500:], r.stderr[-500:]))
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/19（commit だけ・夜の push で公開）：記事3本＝pickup/a/daibakushow.html（DAIBAKUSHOW 2026 東京ガーデンシアター 12/30・一般 11/21 10:00）・asagaya.html（阿佐ヶ谷姉妹 ミーツ オーケストラ グランシップ R9年 2/28・一般 11/22 10:00）・plastictree.html（Plastic Tree 年末公演 カルッツかわさき 12/27・一般 11/21 12:00）→ 台帳・pickup_list --apply・CD/宿ボタン／独立FC＝🔴0🟠1🟡6（指摘4つ直した）・すちこ「OK」\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg.txt', 'pickup', 'tools/pickup_articles.json', D], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('commit rc=%d %s\n' % (r.returncode, r.stderr[-300:]))
out.close()
