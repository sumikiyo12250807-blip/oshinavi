# -*- coding: utf-8 -*-
"""予約済みの投稿の【9/12(土)発売】ブロックを、作り直した素材から組み直して「_v2」ファイルに書く（元のファイルは触らない）。
アーティストごとに1行（group_lists と同じまとめ方）。県のうしろに付いた日付（「三重 11/3〜」）は落とす。
使い方: python tmp/x0912/rebuild_block.py 04 09"""
import io, re, sys
sys.path.insert(0, 'tmp/x0912')
sys.stdout.reconfigure(encoding='utf-8')
import group_lists as G  # noqa
mat = io.open('tmp/x0912/material.md', encoding='utf-8').read()
secs = re.split(r'\n---\n', mat)
DROP = {('11:00', 'みやけん／ヒビキpiano', '')}  # 同じ公演・同じ時刻の先行と重なる行（券種名が「みやけん」だけの行）
for no in sys.argv[1:]:
    i = int(no)
    sec = secs[i - 3]
    m1 = re.search(r'【9/12\(土\)発売】[^\n]*\n(.*?)\n\n', sec, re.S)
    lines = []
    for ln in m1.group(1).splitlines():
        m = G.LINE.match(ln.replace('? ', '時刻未定 ', 1) if ln.startswith('? ') else ln)
        if not m:
            continue
        pref = re.sub(r'\s*\d{1,2}/\d{1,2}〜.*$', '', m.group(3))
        if (m.group(1), m.group(2), m.group(4) or '') in DROP:
            continue
        lines.append('%s %s／%s%s' % (m.group(1), m.group(2), pref, m.group(4) or ''))
    block = G.regroup(lines)
    p = 'tmp/x0912/post%02d.txt' % i
    post = io.open(p, encoding='utf-8-sig').read()
    old = re.search(r'(【9/12\(土\)発売】\n)(.*?)(\n\n)', post, re.S)
    new = post[:old.start(2)] + '\n'.join(block) + post[old.end(2):]
    io.open('tmp/x0912/post%02d_v2.txt' % i, 'w', encoding='utf-8', newline='').write(new)
    ob = set(old.group(2).splitlines())
    print('post%02d: 9/12 %d行 → %d行 ／ %d字 → %d字' % (i, len(ob), len(block), len(post), len(new)))
    for b in block:
        if b not in ob:
            print('   ＋ ' + b)
    for b in sorted(ob - set(block)):
        print('   － ' + b)
