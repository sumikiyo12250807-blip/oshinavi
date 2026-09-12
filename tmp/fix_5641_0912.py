# -*- coding: utf-8 -*-
"""id5641『5秒で完全犯罪を生成する方法』公開記念舞台挨拶／前夜祭 の千秋楽を直す（2026-09-12）。
reconcile の QC-EVDATE＝登録の千秋楽 9/12 が実公演の最終日 9/21 より古い＝明日カードが画面から消える。
値は build_pia_entries がぴあから組んだもの（tmp/built_missing3_0912.json）をそのまま使う（手で作らない）。
日付の欄に残っていた過去の 9/10〜9/12 と終わった会場は、ユーザー決定（終わった公演の日は入れない）に合わせて外れる。
使い方: python tmp/fix_5641_0912.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
b = next(x for x in json.load(io.open('tmp/built_missing3_0912.json', encoding='utf-8-sig')) if x['id'] == 5641)
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 5641)
assert e.get('date') == '2026-09-12', '5641 の千秋楽が想定と違う: %s' % e.get('date')
for k in ('date', 'dateLabel', 'venue', 'prefecture'):
    print('id5641 %-10s %s\n                  → %s' % (k, e.get(k), b.get(k)))
    e[k] = b.get(k)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
