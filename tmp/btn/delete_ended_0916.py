# -*- coding: utf-8 -*-
"""公演が終わったエントリを消す（2026-09-16 深夜・DELETE_GATE の手順どおり）
・対象は引数の id（check_expired の「公演終了」で、別エージェントが「消してよい」と独立に判定したものだけ）
・消す前に予備（index.html.bak_0916_del_ended）
・改行は CRLF のまま（newline=''）
・消した番号は NEW_ORDER からも外し、NEW_ORDER とジャンル new のエントリがぴったり一致するか確かめる
・消したあと「全体の件数＝前−消した数」「ほかのエントリは1文字も変わらない」を確かめる
・logs/removed_2026-09-16.md に 公演名＋最後の公演日＋確認用の直URL（index.html のデータから機械で取り出す）を追記
使い方: python delete_ended_0916.py <id,id,...>
"""
import datetime
import io
import json
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ids = {int(x) for x in sys.argv[1].split(',') if x.strip()}


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


def new_order(text):
    return json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', text, re.S).group(1))


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
by = {e['id']: e for e in ev}
missing = sorted(ids - set(by))
assert not missing, 'index.html に無い id: %s' % missing
shutil.copyfile(P, 'index.html.bak_0916_del_ended')

lines = text.split('\r\n')
out, i, removed = [], 0, []
while i < len(lines):
    if lines[i] == '  {' and i + 1 < len(lines) and lines[i + 1].startswith('    "id": '):
        eid = int(lines[i + 1].split(':')[1].strip().rstrip(','))
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        if eid in ids:
            assert lines[j] == '  },', '配列の最後の要素は想定外: %s' % eid
            removed.append(eid)
            i = j + 1
            continue
    out.append(lines[i])
    i += 1
new = '\r\n'.join(out)
m = re.search(r'(const NEW_ORDER = \[)([^\]]*)(\])', new)
arr = [int(x) for x in m.group(2).split(',') if x.strip()]
gone_in_order = [x for x in arr if x in ids]
new = new[:m.start(2)] + ', '.join(str(x) for x in arr if x not in ids) + new[m.end(2):]

ev2 = events(new)
assert sorted(removed) == sorted(ids), (sorted(removed), sorted(ids))
assert len(ev2) == len(ev) - len(ids)
before = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev if e['id'] not in ids}
after = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev2}
assert before == after, 'ほかのエントリが変わった'
pool = {e['id'] for e in ev2 if e.get('genre') == 'new'}
no = set(new_order(new))
assert no == pool, (sorted(no - pool), sorted(pool - no))
assert new.count('  const NEW_ORDER') == 1

with open(P, 'w', encoding='utf-8', newline='') as f:
    f.write(new)

os.makedirs('logs', exist_ok=True)
log = 'logs/removed_2026-09-16.md'
# 書き方は logs/removed_2026-09-15.md にそろえる（見出し＋説明＋「id｜公演名｜公演日｜会場｜確認用URL」の表）
NOTE = os.environ.get('DEL_NOTE', '')
rows = ['| id | 公演名 | 公演日 | 会場 | 確認用URL |', '|---|---|---|---|---|']
for eid in sorted(ids):
    e = by[eid]
    lk = e.get('links') or {}
    url = next((u for u in [lk.get('pia'), lk.get('eplus'), lk.get('rakuten'), lk.get('lawson')] + [t.get('url') for t in e.get('tickets') or []]
                if isinstance(u, str) and u.startswith('http')), '（URLなし）')
    rows.append('| %d | %s | %s | %s | %s |' % (eid, e.get('name'), e.get('date'), e.get('venue'), url))
with io.open(log, 'a', encoding='utf-8') as f:
    f.write('\n## 公演が終わったため（%d件・%s）\n\n' % (len(ids), datetime.datetime.now().strftime('%H:%M')))
    f.write('別エージェントの独立検証（「削除は誤りという前提で」・index.html のデータで判定）で「消してよい」だった分。%s\n\n' % NOTE)
    f.write('\n'.join(rows) + '\n')
print('消した %d件（全体 %d → %d）／NEW_ORDER から外した %s／新着 %d件と NEW_ORDER が一致' % (len(ids), len(ev), len(ev2), gone_in_order, len(pool)))
print('記録 → %s ／予備 index.html.bak_0916_del_ended' % log)
