# -*- coding: utf-8 -*-
"""朝の発売前スイープ（tmp/sweep_presale_0913/*.json の rows＝一覧の全行）を使って、
**登録済みのぴあページに、ぴあがあとから足した窓**（その発売日の枠がOSHINAVIに無い行）を出す（読むだけ）。
ぴあへの追加の読み込みは0（スイープで読んだ行をそのまま使う）。
memory: feedback_existing_entries_miss_new_windows

出力: tmp/sweep_presale_0913/pia_days_<lg>.txt（tmp/x0912/true_missing.py にそのまま渡せる形）
使い方: python tmp/window_gap_0912.py
      → python tmp/x0912/true_missing.py tmp/sweep_presale_0913/pia_days_01.txt
"""
import collections
import datetime
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DIR = 'tmp/sweep_presale_0913'
TODAY = datetime.date.today().isoformat()

src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
cd2e = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', u):
            cd2e.setdefault(c, e)

by_lg = collections.defaultdict(list)
nrows = 0
for p in sorted(glob.glob(os.path.join(DIR, '*.json'))):
    d = json.load(io.open(p, encoding='utf-8'))
    rows = d.get('rows')
    if rows is None:
        print('⚠️ %s に rows が無い（古い道具で取った？）' % p)
        continue
    nrows += len(rows)
    lg = os.path.basename(p)[:2]
    for r in rows:
        m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', r.get('rlsdate') or '')
        if not m:
            continue  # TODAY（本日発売）はヒールの受け持ち／日付不明は別扱い
        iso = '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
        if iso <= TODAY:
            continue
        cm = re.search(r'event(?:Bundle)?Cd=(\w+)', r.get('url') or '')
        e = cd2e.get(cm.group(1)) if cm else None
        if not e:
            continue  # 未登録ページ＝通常の新着収集が受け持つ
        if any(t.get('startDate') == iso for t in e.get('tickets') or []):
            continue
        by_lg[lg].append((iso, r, e))

tot = 0
for lg, miss in sorted(by_lg.items()):
    seen, uniq = set(), []
    for iso, r, e in sorted(miss, key=lambda x: x[0]):
        k = (iso, r.get('url'), r.get('venue'), r.get('saletype'))
        if k in seen:
            continue
        seen.add(k)
        uniq.append((iso, r, e))
    tot += len(uniq)
    with io.open(os.path.join(DIR, 'pia_days_%s.txt' % lg), 'w', encoding='utf-8') as f:
        f.write('ぴあ lg=%s 登録済みページの発売前の行で、その発売日の枠がOSHINAVIに無い %d件\n' % (lg, len(uniq)))
        for iso, r, e in uniq:
            f.write('  %s %s | %s | %s | 登録あり id%s（その日の枠なし）\n'
                    % (iso, r.get('artist'), r.get('saletype'), r.get('venue'), e['id']))
    print('lg=%s 窓の抜け候補 %d件 → %s/pia_days_%s.txt' % (lg, len(uniq), DIR, lg))
print('読んだ行 %d ／ 抜け候補 合計 %d件（次は true_missing.py で名前＋県＋発売日で絞る）' % (nrows, tot))
