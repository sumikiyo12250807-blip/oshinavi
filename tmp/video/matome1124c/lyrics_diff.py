# -*- coding: utf-8 -*-
# 曲に入っている歌詞（USLT）と、あたしが渡した歌詞（mine.txt）を行ごとに突き合わせる（matome1024j/lyrics_diff.py の形）→ lyrics_diff.txt
import io, difflib, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
raw = io.open(D + 'lyrics_tag.txt', 'rb').read()
for enc in ('utf-8', 'utf-16'):
    try:
        t = raw.decode(enc); break
    except Exception:
        pass
t = t.replace('\x00', '')
uslt = t.split('== USLT', 1)[1]
mine = io.open(D + 'mine.txt', encoding='utf-8').read()
norm = lambda s: [l.strip() for l in s.splitlines() if l.strip()]
a, b = norm(mine), norm(uslt)
out = list(difflib.unified_diff(a, b, 'mine', 'uslt', lineterm='', n=0))
out.append('行数 mine %d uslt %d 違い %s' % (len(a), len(b), 'なし' if not out else 'あり'))
out.append('USLT の最後の行: ' + [l for l in b if not l.startswith('[')][-1])
io.open(D + 'lyrics_diff.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
