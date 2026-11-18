# -*- coding: utf-8 -*-
# 11/18 記事3本（すちこ「OK」）を pickup/a/ に組み、台帳に登録 → pickup_list --apply（鍵の中）→ CD・宿のボタン → commit（push は夜）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1118/art18/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
A = [
 ('zennihon', '全日本表現力選手権', '12/26(土) 19:30 東京・ルミネtheよしもと', '54893'),
 ('elf', 'エルフの好きな人を呼ぶライブ', '12/27(日) 17:00 東京・渋谷よしもと漫才劇場', '54576'),
 ('guiano', 'Guiano', 'R9年 6/12(土) 大阪・UMEDA CLUB QUATTRO／6/13(日) 愛知・NAGOYA CLUB QUATTRO／6/19(土) 東京・SHIBUYA CLUB QUATTRO 各18:00', '43595'),
]
for slug, q, shows, w in A:
    r = subprocess.run([sys.executable, 'tools/pickup_article.py', D + slug + '.md', slug, '--q', q,
                        '--shows-head', '発売になる公演', '--shows', shows, '--watch', w],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d %s %s\n' % (slug, r.returncode, r.stdout.strip(), r.stderr[-500:])); out.flush()
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1118'); os.close(fd); break
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
    '11/18（commit だけ・夜の push で公開）：記事3本＝pickup/a/zennihon.html（全日本表現力選手権〜年末ルミネの会〜 ルミネtheよしもと 12/26・FANY 一般 11/19 10:00）・elf.html（エルフの好きな人を呼ぶライブ「Gal whip」渋谷よしもと漫才劇場 12/27・FANY 一般 11/19 10:00）・guiano.html（Guiano Quattro Tour 2027 R9年 6/12〜6/19・e+ オフィシャル先行 11/19 12:00）→ 台帳・pickup_list --apply・CD/宿ボタン／独立FC＝🔴0🟠1🟡1（2件とも直した）・すちこ「OK」\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
r = subprocess.run([sys.executable, 'tmp/x1112/commit.py', D + 'msg.txt', 'pickup', 'tools/pickup_articles.json', D], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('commit rc=%d %s\n' % (r.returncode, r.stderr[-300:]))
out.close()
