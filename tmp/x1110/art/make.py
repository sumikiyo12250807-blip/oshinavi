# -*- coding: utf-8 -*-
# 記事3本を pickup/a/ に組み、台帳に登録 → pickup_list --apply（index.html を触る＝鍵の中）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1110/art/'
out = io.open(D + 'make.txt', 'w', encoding='utf-8')
A = [
 ('kyary', 'きゃりーぱみゅぱみゅ', 'R9年 3/19(金)〜6/12(土) 神奈川・大阪・福岡・愛知・北海道・広島・東京', '5155'),
 ('lions', '埼玉西武ライオンズ', 'R9年 2/27(土)・2/28(日) 台湾・台北ドーム', '47959'),
 ('ozaki', '尾崎裕哉', 'R9年 4/4(日)〜6/20(日) 全国15都市16公演', '49921'),
]
for slug, q, shows, w in A:
    r = subprocess.run([sys.executable, 'tools/pickup_article.py', D + slug + '.md', slug, '--q', q,
                        '--shows-head', '発売になる公演', '--shows', shows, '--watch', w],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('%s rc=%d %s %s\n' % (slug, r.returncode, r.stdout.strip(), r.stderr[-500:]))
LK = 'tmp/x1110/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_1110'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    r = subprocess.run([sys.executable, 'tools/pickup_list.py', '--apply'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('pickup_list rc=%d\n%s\n%s\n' % (r.returncode, r.stdout[-2000:], r.stderr[-800:]))
finally:
    os.remove(LK)
