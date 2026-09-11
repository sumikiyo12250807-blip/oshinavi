# -*- coding: utf-8 -*-
"""push前の抜き取り（tmp/push_sample_0912.txt の id）について、今朝既存エントリに増えた・書き換わった枠
（tmp/added_windows_0912.txt）が、別エージェントがぴあ実ページからゼロで読んだ枠（scratchpad/push_check_result.json）と
合っているかを見る（読むだけ）。
一致の判定＝登録の枠の「締切(date)」か「発売日(startDate)」が、エージェントの読んだ受付中/発売前の枠の
end か start の日付と一致し、しかもその枠が受付中か発売前であること。
使い方: python tmp/compare_push_sample_0912.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\0fc1d2b7-fccb-457b-879f-7aec070e018d\scratchpad'
res = {r['id']: r for r in json.load(io.open(SP + r'\push_check_result.json', encoding='utf-8'))}
ids = {int(ln.split('\t')[0]) for ln in io.open('tmp/push_sample_0912.txt', encoding='utf-8') if ln.strip()}
added = []
for ln in io.open('tmp/added_windows_0912.txt', encoding='utf-8'):
    m = re.match(r'id(\d+) \| (.*?) \| (.*?) \| date=(\S*) start=(\S*) \| (.*)$', ln.rstrip('\n'))
    if m and int(m.group(1)) in ids:
        added.append((int(m.group(1)), m.group(3), m.group(4), m.group(5)))

ok = bad = unread = 0
for i, ty, d, sd in added:
    r = res.get(i)
    if not r:
        unread += 1
        print('⏭️ id%s 読めていない | %s' % (i, ty))
        continue
    live = [s for s in (r.get('slots') or []) if s.get('state') in ('受付中', '発売前')]
    days = {(s.get('end') or '')[:10] for s in live} | {(s.get('start') or '')[:10] for s in live}
    hit = (d and d in days) or (sd and sd in days)
    if hit:
        ok += 1
    else:
        bad += 1
        print('❌ id%s %s | date=%s start=%s\n     実ページの受付中/発売前: %s'
              % (i, ty, d, sd, ['%s %s〜%s %s' % (s.get('type'), s.get('start'), s.get('end'), s.get('state')) for s in live][:6]))
print('\n抜き取り %d件の枠 %d本 ＝ 一致 %d ／ 食い違い %d ／ 読めていない %d' % (len(ids), len(added), ok, bad, unread))
