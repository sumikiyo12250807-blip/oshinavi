# -*- coding: utf-8 -*-
# 姐さんの動画の決まり（memory 12本＋tmp/video/CHECKLIST.md）を1本 feedback_anesan_video_rules.md にまとめる
#   元の本文はそのまま写す（取りこぼさない）・元のファイルは消す・索引のリンクを付け替える
import io, os, re
M = 'C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
NAMES = ['project_video_asset_helpers', 'feedback_anesan_face_reference', 'feedback_anesan_pose_hair_variety',
         'feedback_costume_matches_background', 'feedback_costume_matches_lyric', 'feedback_same_outfit_motion_pairs',
         'feedback_video_one_sheet_per_video', 'feedback_matome_outro_no_duplicate_char', 'feedback_matome_video_calm_layout',
         'feedback_video_bow_start_end', 'feedback_video_caption_oshinavi_name', 'feedback_tiktok_cover_first_frame']
CK = 'C:/Users/user/oshinavi/tmp/video/CHECKLIST.md'
log = io.open('C:/Users/user/oshinavi/tmp/x1123/songs/merge_mem.txt', 'w', encoding='utf-8')
parts = []
for n in NAMES:
    p = M + n + '.md'
    if not os.path.exists(p):
        log.write('無い %s\n' % n)
        continue
    t = io.open(p, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n?(.*)', t, re.S)
    head, body = (m.group(1), m.group(2)) if m else ('', t)
    desc = re.search(r'^description:\s*(.*)$', head, re.M)
    parts.append((n, desc.group(1).strip() if desc else '', body.strip()))
    log.write('写した %s %d字\n' % (n, len(body)))
ck = io.open(CK, encoding='utf-8').read().split('\n', 1)[1].strip()
out = ['---', 'name: feedback_anesan_video_rules',
       'description: 🎬姐さんの動画の決まりを1本にまとめた（11/23 すちこ「一つにまとめて」）＝作り始める前に頭の点検表を上から全部見る（形がいつもと違っても）。絵の頼み方・顔の見本・髪を1人ずつ・顔の傾き・3コマ・全身・背景・組み立て・見せ方・字幕・カバー',
       'metadata:', '  type: feedback', '---', '',
       '# 姐さんの動画の決まり（ひとつにまとめた・2026-11-23）', '',
       '11/23 すちこ「次から見落とさないで　どうして見落とすことがあるのか」「一つにまとめて」＝決まりが12本の memory に散っていて、字幕スクロールの新しい形の動画で3コマ・顔の傾きを見落とした。**ここ1本だけを見る**。新しい決まりはここに足す（ほかに作らない）。', '',
       '## ✅ 作り始める前の点検表（上から全部）', '', ck, '', '---', '',
       '## 元の決まり（そのまま写した・古い日付の下に新しい訂正がある時は新しい方が正）', '']
for n, d, b in parts:
    b = re.sub(r'^#\s', '### ', b, flags=re.M)
    out += ['## 〔%s〕%s' % (n, d), '', b, '']
io.open(M + 'feedback_anesan_video_rules.md', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
for n, d, b in parts:
    os.remove(M + n + '.md')
os.remove(CK)
# 索引とほかの memory のリンクを付け替える
for f in os.listdir(M):
    if not f.endswith('.md') or f == 'feedback_anesan_video_rules.md':
        continue
    p = M + f
    t = io.open(p, encoding='utf-8').read()
    t2 = t
    for n in NAMES:
        t2 = t2.replace('(%s.md)' % n, '(feedback_anesan_video_rules.md)').replace('[[%s]]' % n, '[[feedback_anesan_video_rules]]')
    t2 = t2.replace('[tmp/video/CHECKLIST.md](C:/Users/user/oshinavi/tmp/video/CHECKLIST.md)', '[feedback_anesan_video_rules.md](feedback_anesan_video_rules.md)')
    if t2 != t:
        io.open(p, 'w', encoding='utf-8').write(t2)
        log.write('リンクを直した %s\n' % f)
log.write('まとめた本の字数 %d\n' % len('\n'.join(out)))
