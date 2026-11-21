# -*- coding: utf-8 -*-
# 11/26(木)発売の素材（まとめの歌詞用）＝ x1121/x/material_1125.py の日付違い
import io, os, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
s = io.open('tmp/x1121/x/material_1125.py', encoding='utf-8').read()
s = s.replace("TOM, D2, D3 = '2026-11-25', '2026-11-26', '2026-11-27'", "TOM, D2, D3 = '2026-11-26', '2026-11-27', '2026-11-28'")
s = s.replace("tmp/x1121/x/material_1125.md", "tmp/x1122/x/material_1126.md").replace('# 11/25(水)発売', '# 11/26(木)発売')
assert "'2026-11-28'" in s and 'material_1126.md' in s
io.open('tmp/x1122/x/material_1126.py', 'w', encoding='utf-8').write(s)
r = subprocess.run([sys.executable, 'tmp/x1122/x/material_1126.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
io.open('tmp/x1122/x/mk_mat1126.txt', 'w', encoding='utf-8').write('%d %s %s' % (r.returncode, r.stdout[-1500:], r.stderr[-800:]))
