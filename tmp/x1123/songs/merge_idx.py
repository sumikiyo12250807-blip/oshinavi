# -*- coding: utf-8 -*-
# MEMORY.md・index_x_sns.md の中で feedback_anesan_video_rules.md を指す行を1行にまとめる
import io
M = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
log = io.open('C:/Users/user/oshinavi/tmp/x1123/songs/merge_idx.txt', 'w', encoding='utf-8')
# MEMORY.md：頭の1行（点検表）だけ残し、🎨 の4行を消す
p = M + 'MEMORY.md'
L = io.open(p, encoding='utf-8').read().split('\n')
keep = [l for l in L if not ('(feedback_anesan_video_rules.md)' in l and l.startswith('- 🎨'))]
log.write('MEMORY.md %d → %d 行\n' % (len(L), len(keep)))
io.open(p, 'w', encoding='utf-8').write('\n'.join(keep))
# index_x_sns.md：動画の決まりだけの行を消し、1行にまとめる（ほかのリンクと同居の行は、その部分だけ1本を指す形のまま残す）
p = M + 'index_x_sns.md'
L = io.open(p, encoding='utf-8').read().split('\n')
out, first = [], True
for l in L:
    only = '(feedback_anesan_video_rules.md)' in l and l.count('](') == l.count('(feedback_anesan_video_rules.md)')
    if only:
        if first:
            out.append('- 🎬🚨🆕 **[姐さんの動画の決まり（12本を1本にまとめた・頭に作る前の点検表）](feedback_anesan_video_rules.md)**（11/23 すちこ「一つにまとめて」）＝顔の見本・髪を1人ずつ・顔の傾き・1枚に9人の全身・透明・3コマ 元→2→3→2・服は背景と歌に・絵コンテの前に9人を見せる・絵コンテ＋試し・落ち着いた見せ方・締めに同じ子を出さない・字幕は推しNAVI・0秒のカバー・お辞儀')
            first = False
        log.write('消した: %s\n' % l[:60])
        continue
    out.append(l)
io.open(p, 'w', encoding='utf-8').write('\n'.join(out))
