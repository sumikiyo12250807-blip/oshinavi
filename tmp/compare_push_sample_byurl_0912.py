# -*- coding: utf-8 -*-
"""昼のpush前の抜き取りの突き合わせ（飛び先URLごと・読むだけ）。
tmp/compare_push_sample_noon_0912.py は「その id に増えた枠の全部」を、エージェントが読んだ1ページの枠と比べていたので、
ツアーの別会場（別の eventCd）の枠が全部「食い違い」に見えた（9/12昼＝50本中ほぼ全部がこの型）。
ここでは、エージェントが実際に読んだURL（抜き取りのURL＋たどったまとめページの中の公演）に付いている枠だけを比べる。
一致の判定は元と同じ＝登録の締切(date)か発売日(startDate)が、受付中/発売前の枠の end か start の日付と一致すること。
使い方: python tmp/compare_push_sample_byurl_0912.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\0fc1d2b7-fccb-457b-879f-7aec070e018d\scratchpad'
res = {r['id']: r for r in json.load(io.open(SP + r'\push_check_noon_result.json', encoding='utf-8'))}


def cd(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else None


read = {}
for ln in io.open('tmp/push_sample_noon_0912.txt', encoding='utf-8'):
    if ln.strip():
        i, u = ln.split('\t')[:2]
        read.setdefault(int(i), set()).add(cd(u))
for i, r in res.items():
    for u in r.get('urls') or []:
        read.setdefault(i, set()).add(cd(u))

ok = bad = skip = unread = 0
bad_rows = []
for ln in io.open('tmp/added_windows_noon_0912.txt', encoding='utf-8'):
    m = re.match(r'id(\d+) \| (.*?) \| (.*?) \| date=(\S*) start=(\S*) \| (.*)$', ln.rstrip('\n'))
    if not m or int(m.group(1)) not in read:
        continue
    i, ty, d, sd, u = int(m.group(1)), m.group(3), m.group(4), m.group(5), m.group(6).strip()
    if cd(u) not in read[i]:
        skip += 1
        continue
    r = res.get(i)
    if not r or r.get('fetch_failed'):
        unread += 1
        continue
    live = [s for s in (r.get('slots') or []) if s.get('state') in ('受付中', '発売前')]
    days = {(s.get('end') or '')[:10] for s in live} | {(s.get('start') or '')[:10] for s in live}
    if (d and d in days) or (sd and sd in days):
        ok += 1
    else:
        bad += 1
        bad_rows.append((i, ty, d, sd, u, ['%s %s〜%s %s' % (s.get('type'), s.get('start'), s.get('end'), s.get('state'))
                                          for s in live][:6]))
for i, ty, d, sd, u, lv in bad_rows:
    print('❌ id%s %s | date=%s start=%s | %s\n     実ページの受付中/発売前: %s' % (i, ty, d, sd, u, lv))
print('\nエージェントが読んだページの枠 %d本 ＝ 一致 %d ／ 食い違い %d ／ 読めていない %d'
      % (ok + bad + unread, ok, bad, unread))
print('（別会場のページ＝エージェントが読んでいない枠 %d本は比べていない）' % skip)
