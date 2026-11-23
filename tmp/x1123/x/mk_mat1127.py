# -*- coding: utf-8 -*-
# 11/27(金)発売の素材（まとめの歌詞用）＝ x1122/x/material_1126.py の日付違い
import io, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
os.makedirs('tmp/x1123/x', exist_ok=True)
s = io.open('tmp/x1122/x/material_1126.py', encoding='utf-8').read()
s = s.replace("TOM, D2, D3 = '2026-11-26', '2026-11-27', '2026-11-28'", "TOM, D2, D3 = '2026-11-27', '2026-11-28', '2026-11-29'")
s = s.replace("tmp/x1122/x/material_1126.md", "tmp/x1123/x/material_1127.md").replace('# 11/26(木)発売', '# 11/27(金)発売')
assert "'2026-11-29'" in s and 'material_1127.md' in s
io.open('tmp/x1123/x/material_1127.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, 'tmp/x1123/x/material_1127.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
io.open('tmp/x1123/x/mk_mat1127.txt', 'w', encoding='utf-8').write('%d %s %s' % (r.returncode, r.stdout[-1500:], r.stderr[-800:]))
