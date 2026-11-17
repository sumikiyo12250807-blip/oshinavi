# -*- coding: utf-8 -*-
# 11/17 記事3本（すちこ「記事OKよ」）を pickup/a/ に組み、台帳に登録 → pickup_list --apply（鍵の中）→ CD・宿のボタン → commit
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1117/art17/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
A = [
 ('minamikousetsu', '南こうせつ', 'R9年 3/27(土) 17:00 東京・調布市グリーンホール 大ホール', '30568'),
 ('danseiburanko', '男性ブランコ', 'R9年 1/7(木)〜1/11(月・祝) 東京・本多劇場', ','.join(str(i) for i in range(49067, 49076))),
 ('hikawakiyoshi', '氷川きよし', 'R9年 3/26(金)・3/28(日) 13:30 鹿児島・宝山ホール／宮崎市民文化ホール', '38644'),
]
for slug, q, shows, w in A:
    r = subprocess.run([sys.executable, 'tools/pickup_article.py', D + slug + '.md', slug, '--q', q,
                        '--shows-head', '発売になる公演', '--shows', shows, '--watch', w],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d %s %s\n' % (slug, r.returncode, r.stdout.strip(), r.stderr[-500:]))
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1117'); os.close(fd); break
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
    '11/17（commit だけ・夜の push で公開）：記事3本＝pickup/a/minamikousetsu.html（南こうせつ コンサートツアー2027 ～君と僕のうた～ 調布 R9年 3/27・e+ 一般 11/19 10:00）・danseiburanko.html（男性ブランコ単独公演「くじら図書館」本多劇場 R9年 1/7〜1/11・FANY 一般 11/19 10:00）・hikawakiyoshi.html（氷川きよし KIINA\'S LAND2 鹿児島 3/26・宮崎 3/28・e+ プレオーダー 11/18 12:00）→ 台帳・pickup_list --apply・CD/宿ボタン／独立FC 2人＝🔴0🟠0（🟡5件を直した）・すちこ「記事OKよ」\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg.txt', 'pickup', 'tools/pickup_articles.json', D], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('commit rc=%d %s\n' % (r.returncode, r.stderr[-300:]))
