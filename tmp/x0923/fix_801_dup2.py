# -*- coding: utf-8 -*-
"""801 八神純子＝二重の外し方を間違えたので入れ替える（2026-09-16 朝）。
ぴあの実ページは「大阪・兵庫 9/29〜9/30」を**1枚のカード**で出している（reconcile の QC-PREF / QC-PERF がそう言った）。
  戻す（正）: 一般発売（大阪・兵庫 9/29〜9/30公演）〜9/22 23:59
  外す（誤）: 一般発売（大阪 9/29・兵庫 9/30公演）〜9/22 23:59   ← 今朝の取り直しで入った形・ぴあの表記と違う
飛び先はどちらも eventCd=2612266。
使い方: python tmp/x0923/fix_801_dup2.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 801
KEEP = '一般発売（大阪・兵庫 9/29〜9/30公演）〜9/22 23:59'
DROP = '一般発売（大阪 9/29・兵庫 9/30公演）〜9/22 23:59'

src = io.open(P, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
drop = [t for t in e['tickets'] if t['type'] == DROP]
assert len(drop) == 1 and not [t for t in e['tickets'] if t['type'] == KEEP], '前提が違う'
url = drop[0].get('url')
i = e['tickets'].index(drop[0])
e['tickets'][i] = {'type': KEEP, 'date': '2026-09-22', 'url': url}
print('id801 入れ替えた＝残す「%s」／外す「%s」（飛び先 %s）' % (KEEP, DROP, (url or '')[-22:]))
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_801dup2')
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + m.group(3) + src[m.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
