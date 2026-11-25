# -*- coding: utf-8 -*-
# 11/25 記事3本（すちこ「記事3本よ」＝OK）を pickup/a/ に組み、台帳に登録 → pickup_list --apply（鍵の中）→ CD・宿のボタン
#  → カードの記事ボタン（pickup_card_links --apply --lock＝自分で鍵を取る）→ 画面の番人 → commit（push は夜）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1125/art25/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
def run(a, tag):
    r = subprocess.run(a if a[0] == 'node' else [sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d\n%s\n%s\n' % (tag, r.returncode, r.stdout[-2000:], r.stderr[-800:])); out.flush()
    return r.returncode
A = [
 ('harunoutaikai', '春の謡会', 'R9年 1/30(土)・1/31(日) 16:00 大阪・大槻能楽堂', '36535,36536'),
 ('mayj_kidsjazz', 'May J.', 'R9年 3/7(日) 15:00 大阪・枚方市総合文化芸術センター 関西医大 大ホール', '45838'),
 ('tokiasako', '土岐麻子', 'R9年 2/21(日) 16:00 神奈川・ヨコスカ・ベイサイド・ポケット', '52883'),
]
for slug, q, shows, w in A:
    run(['tools/pickup_article.py', D + slug + '.md', slug, '--q', q, '--shows-head', '発売になる公演', '--shows', shows, '--watch', w], slug)
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1125'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    run(['tools/pickup_list.py', '--apply'], 'pickup_list')
finally:
    os.remove(LK)
run(['tools/pickup_cd_btn.py'], 'pickup_cd_btn')
run(['tools/pickup_card_links.py', '--apply', '--lock', LK], 'pickup_card_links')
rc = run(['node', 'tools/gate_badge_render.js'], 'render')
s = io.open('index.html', encoding='utf-8', newline='').read()
out.write('CRCRLF %d\n' % s.count('\r\r\n'))
io.open(D + 'msg.txt', 'w', encoding='utf-8').write(
    '11/25（commit だけ・夜の push で公開）：記事3本＝pickup/a/harunoutaikai.html（春の謡会2027 大槻能楽堂 R9年 1/30・1/31・一般 11/28 10:00）・mayj_kidsjazz.html（Kids meet Jazz! with May J. 枚方 R9年 3/7・e+ 11/26 10:00）・tokiasako.html（土岐麻子 Yokosuka Bayside Breeze vol.8 R9年 2/21・e+ 11/29 10:00）'
    ' → 台帳・pickup_list --apply・CD/宿ボタン・カードの記事ボタン／独立FC＝🔴0🟠1🟡6（直した）・May J. の「味わう」→「学べる」・すちこ「記事3本よ」（OK）\n\n'
    'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01FQDm48dAXPgAGoNjRP5MVi\n')
if rc == 0:
    run(['tmp/x1112/commit.py', D + 'msg.txt', 'pickup', 'tools/pickup_articles.json', 'index.html', D], 'commit')
else:
    out.write('画面の番人が止めた＝commit しない\n')
out.close()
