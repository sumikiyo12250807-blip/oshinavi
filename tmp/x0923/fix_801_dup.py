# -*- coding: utf-8 -*-
"""801 八神純子＝同じ枠が2つの書き方で二重になっているので、古い形の1枠を外す（2026-09-16 朝）。
  古い形（外す）: 一般発売（大阪・兵庫 9/29〜9/30公演）〜9/22 23:59
  新しい形（残す）: 一般発売（大阪 9/29・兵庫 9/30公演）〜9/22 23:59   ← 今朝の取り直しで入った形
飛び先はどちらも同じ eventCd=2612266（＝飛び先が違えば畳まない決まりに触れない）。
reconcile は「登録10／ぴあ買える9」と出ていた。外したあとに 9=9 になることを確かめる。
使い方: python tmp/x0923/fix_801_dup.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 801
OLD = '一般発売（大阪・兵庫 9/29〜9/30公演）〜9/22 23:59'
NEW = '一般発売（大阪 9/29・兵庫 9/30公演）〜9/22 23:59'

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
old = [t for t in e['tickets'] if t['type'] == OLD]
new = [t for t in e['tickets'] if t['type'] == NEW]
assert len(old) == 1 and len(new) == 1, (len(old), len(new))
assert old[0].get('url') == new[0].get('url'), (old[0].get('url'), new[0].get('url'))
assert not old[0].get('soldout') and not new[0].get('soldout')
e['tickets'] = [t for t in e['tickets'] if t is not old[0]]
print('id801 枠 %d → %d（外した＝%s ／ 残した＝%s ／ 飛び先はどちらも %s）' % (
    len(e['tickets']) + 1, len(e['tickets']), OLD, NEW, (new[0].get('url') or '')[-22:]))
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_801dup')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
