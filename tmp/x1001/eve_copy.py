# -*- coding: utf-8 -*-
# 朝のぴあ発売前スイープの道具を tmp/x1001/eve/ に写す（パスだけ eve に変える＝朝のファイルを上書きしない）
import io, os
root = 'C:/Users/user/oshinavi/'
os.makedirs(root + 'tmp/x1001/eve', exist_ok=True)
for f in ('pia_presale_sweep.py', 'split.py', 'run_build.py', 'filter_built.py', 'pick_new.py', 'merge_add.py'):
    s = io.open(root + 'tmp/x1001/' + f, encoding='utf-8').read()
    s = s.replace('tmp/x1001/', 'tmp/x1001/eve/')
    io.open(root + 'tmp/x1001/eve/' + f, 'w', encoding='utf-8').write(s)
print('ok')
