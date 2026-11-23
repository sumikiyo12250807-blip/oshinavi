# -*- coding: utf-8 -*-
# 使い方: python tmp/x1112/commit.py <メッセージのファイル（Co-Authored-By 込み）> [追加ファイル...]
#   index.html・artists.html・sitemap.xml・artist/・ai_*.html・ai.html・logs/・plan.md・tools/artist_*.json と指定ファイルを add して commit（鍵を持つ）
import subprocess, os, sys, io, glob, time
os.chdir('C:/Users/user/oshinavi')
LK = 'tmp/x1112/index.lock'
while True:   # 🆕11/23 鍵は O_CREAT|O_EXCL で取る（exists を見てから書くと、間に別の道具が入れる）
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'commit'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    files = ['index.html', 'artists.html', 'sitemap.xml', 'artist', 'ai.html', 'logs', 'plan.md',
             'tools/artist_pages.json', 'tools/artist_rest.json'] + glob.glob('ai_*.html') + sys.argv[2:]
    a = subprocess.run(['git', 'add', '--'] + [f for f in files if os.path.exists(f)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    c = subprocess.run(['git', 'commit', '-F', sys.argv[1]], capture_output=True, text=True, encoding='utf-8', errors='replace')
    io.open('tmp/x1112/commit.txt', 'w', encoding='utf-8').write(f'add {a.returncode} {a.stderr[-300:]}\ncommit {c.returncode}\n{c.stdout[-500:]}\n{c.stderr[-300:]}')
finally:
    os.remove(LK)
