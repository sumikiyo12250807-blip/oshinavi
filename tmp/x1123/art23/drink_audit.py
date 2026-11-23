# -*- coding: utf-8 -*-
# 11/18〜11/21 の記事の材料に出ていたドリンク代の文と、その日の記事の本文に入っているか
import io, os, re, glob
R = 'C:/Users/user/oshinavi/tmp/'
o = io.open(R + 'x1123/art23/drink_audit.txt', 'w', encoding='utf-8')
for d in ('x1118/art18', 'x1119/art19', 'x1120/art20', 'x1121/art21'):
    o.write('\n## %s\n' % d)
    for f in sorted(glob.glob(R + d + '/*.txt')) + sorted(glob.glob(R + d + '/*material*.md')):
        t = io.open(f, encoding='utf-8', errors='replace').read()
        hits = sorted({re.sub(r'\s+', ' ', m.group(0)) for m in re.finditer(r'.{0,50}(?:ドリンク|\b1D\b|１Ｄ).{0,40}', t)})
        for h in hits[:6]:
            o.write('  %s: %s\n' % (os.path.basename(f), h))
    for f in sorted(glob.glob(R + d + '/*.md')):
        b = os.path.basename(f)
        if b in ('brief.md', 'sources.md', 'fc.md', 'fc_brief.md') or 'material' in b:
            continue
        t = io.open(f, encoding='utf-8').read()
        o.write('  本文 %s ドリンクの字=%s\n' % (b, 'ドリンク' in t))
