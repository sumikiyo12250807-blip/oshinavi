# -*- coding: utf-8 -*-
# 10/31 夜 すちこ「artistページ残す形でお願い」：すでに消えた artist/<番号>.html を git の履歴から読み戻し、
#   「受付中なし」で残すページの元（tools/artist_rest.json＝番号→名前・最後に載せた公演）を作る
#   最後に消えたコミットの1つ前の版を読む（git cat-file --batch）・名前の番人（SKIP_NAME・ジャンル名・公演名そのもの）に当たる名前は戻さない
import html, io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import build_artist_pages as B

log = subprocess.run(['git', 'log', '--diff-filter=D', '--no-renames', '--name-only', '--format=@%H %cI', '--', 'artist/'],
                     capture_output=True, text=True, encoding='utf-8').stdout
last = {}                                   # 番号 → (消えたコミット, 日時)＝新しい順なので最初に出た方
cur = None
for l in log.splitlines():
    if l.startswith('@'):
        h, d = l[1:].split(' ', 1)
        cur = (h, d)
    else:
        m = re.fullmatch(r'artist/(\d+)\.html', l.strip())
        if m and m.group(1) not in last:
            last[m.group(1)] = cur
reg = json.load(io.open(B.REG, encoding='utf-8'))
nums = {str(v): k for k, v in reg.items()}
gone = [n for n in last if not os.path.exists(f'artist/{n}.html') and n in nums]
print('消えた番号', len(last), '今もファイル無し＋台帳にある', len(gone))

p = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
REST, skip = {}, []
for n in gone:
    h, d = last[n]
    p.stdin.write(f'{h}^:artist/{n}.html\n'.encode()); p.stdin.flush()
    head = p.stdout.readline().decode()
    if head.endswith('missing\n'):
        skip.append((n, 'missing')); continue
    size = int(head.split()[2])
    body = p.stdout.read(size).decode('utf-8', 'replace'); p.stdout.read(1)
    m = re.search(r'<h1>(.*?) のチケット発売日</h1>', body)
    if not m:
        skip.append((n, 'no h1')); continue
    name = html.unescape(m.group(1))
    evs = []
    for en, ev in re.findall(r'<div class="n">(.*?)</div>\s*<div class="v">(.*?)</div>', body):
        evs.append({'n': html.unescape(en), 'v': html.unescape(ev)})
    if B.norm(name) != nums[n]:
        skip.append((n, 'name≠台帳 ' + name)); continue
    if not name.startswith('『') and not name.startswith('ミュージカル『'):
        if B.SKIP_NAME.search(name) or name.lower() in B.GENRE_WORDS or any(B.norm(name) == B.norm(e['n']) for e in evs):
            skip.append((n, '名前の番人 ' + name)); continue
    REST[n] = {'name': name, 'evs': evs[:5], 'genre': '', 'since': d[:10]}
p.stdin.close(); p.wait()
old = {}
if os.path.exists(B.REST):
    old = json.load(io.open(B.REST, encoding='utf-8'))
for k, v in REST.items():
    old.setdefault(k, v)
json.dump(old, io.open(B.REST, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
io.open('tmp/growth1031/backfill_rest.txt', 'w', encoding='utf-8').write(
    f'戻す {len(REST)} / 戻さない {len(skip)}\n' + '\n'.join(f'{a} {b}' for a, b in skip) + '\n')
print('戻す', len(REST), '戻さない', len(skip))
print('16814' in REST, REST.get('16814'))
