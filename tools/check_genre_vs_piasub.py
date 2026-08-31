# -*- coding: utf-8 -*-
"""_piaSub（ぴあが言っている区分）と genre（うちの表示ジャンル）が食い違うエントリを洗い出す。

🚨2026-08-31 新設。アークラ大サーカス(id2527)＝_piaSub「イベントその他」なのに genre が engeki で、
   演劇タブのノイズになっていた（ユーザーがX投稿の下書きを見て発見）。
   ぴあの言うとおりに機械で写すのが原則（memory: feedback_genre_pia_asis_and_other）。
"""
import json, re, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import genre_from_subcat

s = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', s, re.S).group(1))
bad = []
for e in ev:
    sub = e.get('_piaSub')
    if not sub:
        continue
    parts = sub.split('/')
    lg, sc = (parts[0], parts[-1]) if len(parts) > 1 else ('', parts[0])
    try:
        want, extra = genre_from_subcat(lg, sc, e.get('artist', ''))
    except Exception:
        continue
    if not want:
        continue
    now = e.get('genre')
    if now in ('new',):          # 新着プールは振り分け前なので対象外
        continue
    if now != want:
        bad.append((e['id'], e.get('artist', '')[:32], sub, now, want))
print('_piaSub と genre が食い違うエントリ: %d件 / 全%d件' % (len(bad), len(ev)))
for b in bad:
    print('  id%-5s %-34s ぴあ[%s] 今[%s] → 本来[%s]' % (b[0], b[1], b[2], b[3], b[4]))
sys.exit(1 if bad else 0)
