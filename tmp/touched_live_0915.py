# -*- coding: utf-8 -*-
"""今朝さわった「公開中のエントリ」（genre が new 以外）を、朝いちのコミットと今の index.html で比べて出す（読むだけ・2026-09-15）。
push 前の照合（reconcile_pia --ids）と、別エージェントの抜き取りチェックの対象を決めるため。
比べる相手＝e63ee526（9/14夜の最後・今朝の作業の前）。
使い方: python tmp/touched_live_0915.py
出力: tmp/touched_live_ids_0915.txt（カンマ区切り）＋ tmp/touched_live_pick_0915.txt（抜き取り用「id<TAB>名前<TAB>URL…」）
"""
import io
import json
import random
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'e63ee526'


def events(text):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


old = events(subprocess.run(['git', 'show', BASE + ':index.html'], capture_output=True).stdout.decode('utf-8'))
now = events(io.open('index.html', encoding='utf-8').read())
changed = []
for i, e in now.items():
    if e.get('genre') == 'new' or i not in old:
        continue
    if json.dumps(old[i].get('tickets'), ensure_ascii=False, sort_keys=True) != json.dumps(e.get('tickets'), ensure_ascii=False, sort_keys=True) \
            or old[i].get('date') != e.get('date') or old[i].get('dateLabel') != e.get('dateLabel'):
        changed.append(i)
changed.sort()
io.open('tmp/touched_live_ids_0915.txt', 'w', encoding='utf-8').write(','.join(map(str, changed)))


def pia_urls(e):
    us = []
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        if u and 'pia.jp' in u and u not in us:
            us.append(u)
    return us


pick = [i for i in changed if pia_urls(now[i])]
rnd = random.Random(915)
sample = sorted(rnd.sample(pick, min(30, len(pick))))
with io.open('tmp/touched_live_pick_0915.txt', 'w', encoding='utf-8') as f:
    for i in sample:
        f.write('%s\t%s\t%s\n' % (i, (now[i].get('name') or '')[:50], '\t'.join(pia_urls(now[i]))))
deleted = sorted(set(old) - set(now))
print('今朝さわった公開中のエントリ %d件（ぴあURLあり %d）→ tmp/touched_live_ids_0915.txt ／ 抜き取り %d件 → tmp/touched_live_pick_0915.txt ／ 消したエントリ %d件' % (
    len(changed), len(pick), len(sample), len(deleted)))
