# -*- coding: utf-8 -*-
# 歌う5公演の登録を index.html から読む（読むだけ）→ look_ids.txt
import io
R = 'C:/Users/user/oshinavi/'
IDS = ['42567', '42757', '45419', '50748', '49856']
lines = io.open(R + 'index.html', encoding='utf-8').read().split('\n')
out = []
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('"id":') and s[5:].strip().rstrip(',') in IDS:
        j = i
        blk = []
        while j < len(lines) and not (lines[j].startswith('  }') and j > i):
            blk.append(lines[j])
            j += 1
        out.append('== line %d' % (i + 1))
        out += [b for b in blk if '"amazon"' not in b]
io.open(R + 'tmp/video/matome1124c/look_ids.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
