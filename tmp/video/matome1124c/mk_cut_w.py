# -*- coding: utf-8 -*-
# cut_alpha9.py → cut_w.py（冬雪の子・1536×1024・行の切れ目は 300〜420／600〜720・列は 430〜560／930〜1060 で探す）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_alpha9.py', encoding='utf-8').read()
a = "R = [0, cut_at(FG.sum(axis=1), 340, 480), cut_at(FG.sum(axis=1), 740, 890), H]"
b = "C = [0, cut_at(FG.sum(axis=0), 340, 480), cut_at(FG.sum(axis=0), 760, 900), W]"
assert a in s and b in s
s = s.replace(a, "R = [0, cut_at(FG.sum(axis=1), 300, 420), cut_at(FG.sum(axis=1), 600, 720), H]")
s = s.replace(b, "C = [0, cut_at(FG.sum(axis=0), 430, 560), cut_at(FG.sum(axis=0), 930, 1060), W]")
s = s.replace('# 11/4 第4版の切り抜き', '# 11/12 冬雪の子（cut_alpha9 の写し・切れ目の探す範囲だけ変えた）／元：11/4 第4版の切り抜き', 1)
io.open(D + 'cut_w.py', 'w', encoding='utf-8').write(s)
print('ok')
