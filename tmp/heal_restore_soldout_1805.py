# -*- coding: utf-8 -*-
"""heal_blocked_keep_soldout_1805.py の取りこぼしを戻す（2026-09-14 夜）。
あの道具は「売り切れの枠は締切が今日以降だけ残す」にしていたが、売り切れ枠は締切が過去でも
「予定枚数終了」として画面に出し続けている（visible_slot は soldout を常に表示）。
＝9件で HEAD に出ていた売り切れ枠を消してしまった（3853 阪神 12→2枠・4690 C&K 16→4枠・4272 DeNA 1→0枠）。
HEAD にあって現物に無い「売り切れの印付きの枠」を、そのまま書き戻す。
使い方: python tmp/heal_restore_soldout_1805.py [--apply]
"""
import datetime
import io
import json
import re
import subprocess
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
IDS = [756, 1141, 3594, 3853, 3875, 4272, 4690, 7130, 7191]
head_txt = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')
head = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', head_txt, re.S).group(1))}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

for i in IDS:
    e = by[i]
    have = {H.slot_key(t) for t in e['tickets']}
    back = [t for t in head[i]['tickets'] if t.get('soldout') and H.slot_key(t) not in have]
    e['tickets'] = e['tickets'] + back
    vis = [t for t in e['tickets'] if H.visible_slot(t, TODAY)]
    print('id%-5s %s ｜戻す %d枠 → 出る枠 %d（HEAD %d）' % (
        i, (e.get('name') or '')[:24], len(back), len(vis),
        len([t for t in head[i]['tickets'] if H.visible_slot(t, TODAY)])))
    if i == 4272:
        for t in e['tickets']:
            print('     ', t.get('type'), '｜締切', t.get('date'), '｜発売', t.get('startDate'),
                  '｜売り切れ' if t.get('soldout') else '', H._url_id(t.get('url')))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
