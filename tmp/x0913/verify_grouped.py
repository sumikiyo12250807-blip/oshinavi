# -*- coding: utf-8 -*-
"""まとめ直した投稿のリストが、素材（tmp/x0913/material.md）の行を1つも落としていないか確かめる（読むだけ）。
素材の各行（時刻・名前・県・先行）を、投稿側の「時刻 名前／県・県…」に展開したものと突き合わせる。"""
import glob, io, re, sys
sys.path.insert(0, 'tmp/x0913')
sys.stdout.reconfigure(encoding='utf-8')
from group_lists import ALIAS, LINE  # noqa: E402

PREF_FIX = {'京': '京都'}


def rows_of(lines):
    s = set()
    for ln in lines:
        m = LINE.match(ln.replace('?', '時刻未定', 1) if ln.startswith('? ') else ln)
        if not m:
            continue
        t, name, prefs, senko = m.group(1), ALIAS.get(m.group(2), m.group(2)), m.group(3), m.group(4) or ''
        prefs = re.sub(r'\s*\d{1,2}/\d{1,2}〜.*$', '', prefs)
        for p in prefs.split('・'):
            p = PREF_FIX.get(p, p)
            if p == '全国':
                p = '配信'
            s.add((t, name, p, senko))
    return s


mat = io.open('tmp/x0913/material.md', encoding='utf-8').read()
posts = ''.join(io.open(f, encoding='utf-8-sig').read() + '\n' for f in sorted(glob.glob('tmp/x0913/post0[4-9].txt')))
A = rows_of(mat.splitlines())
B = rows_of(posts.splitlines())
miss = sorted(A - B)
extra = sorted(B - A)
print('素材 %d組 ／ 投稿 %d組 ／ 落ちた %d ／ 素材に無い %d' % (len(A), len(B), len(miss), len(extra)))
for x in miss[:30]:
    print('  落ちた', x)
for x in extra[:30]:
    print('  素材に無い', x)
