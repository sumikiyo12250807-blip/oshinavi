# -*- coding: utf-8 -*-
"""新着プール(genre:"new")を _genre（ぴあの区分を機械で写した下書き）へ振り分ける。
決まり＝ぴあの言う通りに写す・人が最終判断する枠を作らない（memory feedback_genre_pia_asis_and_other）。
🚨 保留id（迷った件）は振り分けずプールに残す（memory feedback_new_pool_ok_before_assign）。

使い方:
  python tmp/assign_apply_0913.py            # 一覧だけ（書き換えない）
  python tmp/assign_apply_0913.py --apply    # 適用
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 迷った件＝振り分けずプールに残す（理由は報告と plan.md に書く）
HOLD = {
    8172,  # 瑛人×SANIMYOK PUAN Live2026＝ぴあの区分は「演歌・邦楽」だが瑛人はJ-POP。中身を見てから
    7558,  # Tommy february6 豪華アナログBOX＝9/12の照合でSTALE（決着していない）
    7946,  # 源 上映会＝ぴあのeventCdが無効・他の売り場も見つからない（ユーザーに聞いている最中）
}
# 語彙の穴で enka に落ちていた子（2026-09-13 に HOGAKU_RE へ「和洋楽器」を足して再判定）
OVERRIDE = {
    8281: 'hougaku',  # 和洋楽器ユニット「蒼ノトキ」ライブ
}

APPLY = '--apply' in sys.argv
path = 'index.html'
src = io.open(path, encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

targets = []
for e in ev:
    if e.get('genre') != 'new':
        continue
    if e['id'] in HOLD:
        continue
    g = OVERRIDE.get(e['id']) or e.get('_genre')
    if not g:
        continue
    targets.append((e['id'], g, e.get('name') or '', (e.get('links') or {}).get('pia') or ''))

print('新着 %d件 / 振り分ける %d件 / 保留 %d件' % (
    sum(1 for e in ev if e.get('genre') == 'new'), len(targets), len(HOLD)))

if not APPLY:
    for i, g, n, u in targets[:10]:
        print('  id%-5s -> %-9s %s' % (i, g, n[:34]))
    print('  …（--apply で適用）')
    sys.exit(0)

# 🚨 現物編集＝該当エントリの "genre": "new" の1行だけを書き換える（id据え置き・並び順は動かさない）
out = src
done = 0
for i, g, n, u in targets:
    # そのidのエントリブロックを探して、その中の "genre": "new" を置き換える
    m = re.search(r'(\n    \{\n(?:.*?\n)*?      "id": %d,\n(?:.*?\n)*?)      "genre": "new",' % i, out)
    if not m:
        print('⚠️ id%s のブロックが見つからない＝書き換えていない' % i)
        continue
    out = out[:m.start()] + m.group(1) + '      "genre": "%s",' % g + out[m.end():]
    done += 1

if done != len(targets):
    print('⚠️ %d/%d しか書き換えていない＝適用を中止する' % (done, len(targets)))
    sys.exit(1)

# 書き戻す前に JSON として読めるか・件数が合うかを確かめる
ev2 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', out, re.S).group(1))
left = sum(1 for e in ev2 if e.get('genre') == 'new')
if len(ev2) != len(ev):
    print('⚠️ エントリ件数が変わった %d→%d＝中止' % (len(ev), len(ev2)))
    sys.exit(1)
io.open(path, 'w', encoding='utf-8', newline='').write(out)
print('✅ %d件を振り分けた。新着プールの残り %d件' % (done, left))
