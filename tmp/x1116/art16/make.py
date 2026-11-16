# -*- coding: utf-8 -*-
# 11/16 記事3本を pickup/a/ に組み、台帳に登録 → pickup_list --apply（鍵の中）→ CD・宿のボタン（tmp/x1113/art13/make.py の形）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1116/art16/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
A = [
 ('takahashiyu', '高橋優', 'R9年 5/28(金) 18:30 北海道・カナモトホール', '50748'),
 ('freedomofchoice', 'FREEDOM OF CHOICE', 'R9年 1/12(火)〜2/14(日) 東京・シアタークリエ', '53678'),
 ('sumidabasho', '大相撲すみだ場所', 'R9年 4/14(水) 9:00 東京・ひがしんアリーナ', '52442'),
]
for slug, q, shows, w in A:
    r = subprocess.run([sys.executable, 'tools/pickup_article.py', D + slug + '.md', slug, '--q', q,
                        '--shows-head', '発売になる公演', '--shows', shows, '--watch', w],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d %s %s\n' % (slug, r.returncode, r.stdout.strip(), r.stderr[-500:]))
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1116'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    r = subprocess.run([sys.executable, 'tools/pickup_list.py', '--apply'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('pickup_list rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-2000:], r.stderr[-800:]))
finally:
    os.remove(LK)
r = subprocess.run([sys.executable, 'tools/pickup_cd_btn.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
out.write('pickup_cd_btn rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-1500:], r.stderr[-500:]))
