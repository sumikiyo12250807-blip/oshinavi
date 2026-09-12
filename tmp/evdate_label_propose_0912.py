# -*- coding: utf-8 -*-
"""千秋楽(date)だけ直した63件の、日付の欄(dateLabel)を見直すための材料を並べる（読むだけ・2026-09-12 昼）。
決まり＝終わった公演の日は入れない／これからの公演は売り切れでも入れる（memory feedback_show_true_dates_not_sellable_range）。
各エントリについて、枠の券種名「（… M/D公演）」から、今日以降の公演日と、その括弧の中身（県・会場の手がかり）を出す。
使い方: python tmp/evdate_label_propose_0912.py
出力: tmp/evdate_label_propose_0912.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-12'
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
ids = [int(m) for m in re.findall(r'^id(\d+) \|', io.open('tmp/evdate_label_todo_0912.txt', encoding='utf-8').read(), re.M)]


def shows(ty):
    m = re.search(r'（([^（）]*)公演）', ty or '')
    if not m:
        return []
    inner, out, y = m.group(1), [], 2026
    for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', inner):
        if r9:
            y = 2027
        out.append(('%04d-%02d-%02d' % (y, int(mo), int(dd)), inner))
    return out


lines = []
for i in ids:
    e = ev.get(i)
    if not e:
        lines.append('id%s ⚠️ もう無い' % i)
        continue
    per = {}
    for t in e.get('tickets') or []:
        for d, inner in shows(t.get('type')):
            per.setdefault(d, set()).add(re.sub(r'\s*R9年\s*|\s*\d{1,2}/\d{1,2}[・、]?', ' ', inner).strip())
    fut = sorted(d for d in per if d >= TODAY)
    past = sorted(d for d in per if d < TODAY)
    lines.append('id%s | %s | date=%s' % (i, (e.get('name') or '')[:40], e.get('date')))
    lines.append('   今: %s' % (e.get('dateLabel') or ''))
    lines.append('   venue: %s' % (e.get('venue') or '')[:80])
    lines.append('   これからの公演日: %s' % ' '.join('%s[%s]' % (d[5:], '/'.join(sorted(per[d]))[:24]) for d in fut))
    if past:
        lines.append('   終わった公演日(枠に残っている): %s' % ' '.join(d[5:] for d in past))
io.open('tmp/evdate_label_propose_0912.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('%d件 → tmp/evdate_label_propose_0912.txt' % len(ids))
