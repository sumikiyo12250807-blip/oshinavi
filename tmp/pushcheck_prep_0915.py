# -*- coding: utf-8 -*-
"""push前の抜き取り30件（scratchpad/pushcheck0915/result.json）に、突き合わせ道具が読む "state" を足す（読むだけ・2026-09-15 昼）。
検証係は state_text（ぴあの文言そのまま）だけを書いた。deadline_cover は state が「受付中」「発売前」の区分を「買える」とみる。
  販売期間中／抽選受付中／本日発売初日／受付中 → 受付中
  発売前                                    → 発売前
  それ以外（予定枚数終了・受付終了・販売終了・抽選受付終了・抽選結果発表前 など） → 終了
使い方: python tmp/pushcheck_prep_0915.py
出力: scratchpad/pushcheck0915/pushcheck_T_result.json
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\9f3148c0-6b8e-4c5b-9f93-e5e96670181f\scratchpad\pushcheck0915'
rows = json.load(io.open(os.path.join(SP, 'result.json'), encoding='utf-8'))
cnt = {}
for r in rows:
    for s in r.get('slots') or []:
        tx = s.get('state_text') or ''
        if any(k in tx for k in ('販売期間中', '抽選受付中', '本日発売初日')) or tx.startswith('受付中'):
            st = '受付中'
        elif '発売前' in tx:
            st = '発売前'
        else:
            st = '終了'
        s['state'] = st
        cnt[st] = cnt.get(st, 0) + 1
json.dump(rows, io.open(os.path.join(SP, 'pushcheck_T_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%d件 ／ 区分 %s → pushcheck_T_result.json' % (len(rows), ' '.join('%s%d' % kv for kv in sorted(cnt.items()))))
