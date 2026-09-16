# -*- coding: utf-8 -*-
"""push 前の抜き取り（2026-09-16 朝）＝公開済み（origin/main）から中身が変わった「公開中」のエントリを選び、
別エージェントに渡す「id とぴあのURLだけ」の一覧を作る（登録値は出さない＝独立の読み直し）。
必ず入れる＝今朝の手当ての目立つ所（7618 鈴木雅之・5717 一青窈・8544・8573・9946・3853・4058・1202・8704・3635）。残りは無作為。
使い方: python tmp/push_sample_0916.py [件数]
出力: scratchpad/push_sample_0916.txt（id<TAB>URL…）
"""
import io
import json
import random
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
MUST = [7618, 5717, 8544, 8573, 9946, 3853, 4058, 1202, 8704, 3635]


def events(t):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', t, re.S).group(1))}


old = events(subprocess.run(['git', 'show', 'origin/main:index.html'], capture_output=True).stdout.decode('utf-8'))
cur = events(io.open('index.html', encoding='utf-8').read())
changed = [i for i, e in cur.items() if e.get('genre') != 'new' and i in old
           and json.dumps(e.get('tickets'), ensure_ascii=False, sort_keys=True) != json.dumps(old[i].get('tickets'), ensure_ascii=False, sort_keys=True)
           and old[i].get('genre') != 'new']


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in us:
            us.append(u)
    return us


pick = [i for i in MUST if i in cur]
rest = [i for i in changed if i not in pick and pia_urls(cur[i])]
random.seed(916)
pick += random.sample(rest, max(0, min(len(rest), N - len(pick))))
with io.open(SP + r'\push_sample_0916.txt', 'w', encoding='utf-8') as f:
    for i in pick:
        f.write('%s\t%s\n' % (i, ' '.join(pia_urls(cur[i]))))
print('公開中で枠が変わったエントリ %d件 → 抜き取り %d件 → scratchpad/push_sample_0916.txt' % (len(changed), len(pick)))
