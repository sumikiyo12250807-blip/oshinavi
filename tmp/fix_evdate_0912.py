# -*- coding: utf-8 -*-
"""千秋楽（date）が枠の公演日より古いエントリの date だけを、枠のいちばん後の公演日に直す（2026-09-12 昼）。
reconcile の QC-EVDATE（ev.date が実公演の千秋楽より古い＝画面から消える）と同じ型を、全エントリで一度に直す。
決まり＝エントリの date は千秋楽（memory feedback_longrun_event）。
🚨dateLabel は触らない＝書き方がばらばら（「2026年9月〜12月 全国ツアー」等）で機械で書き換えると崩す恐れ。
   直す候補は tmp/evdate_label_todo_0912.txt に残して、夜に1件ずつ見る。
使い方: python tmp/fix_evdate_0912.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))


def show_dates(ty):
    mm = re.search(r'（([^（）]*)公演）', ty or '')
    out, y = [], 2026
    if not mm:
        return out
    for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', mm.group(1)):
        if r9:
            y = 2027
        out.append('%04d-%02d-%02d' % (y, int(mo), int(dd)))
    return out


rows = []
for e in events:
    d = e.get('date') or ''
    mx = max((x for t in (e.get('tickets') or []) for x in show_dates(t.get('type'))), default='')
    if mx and mx > d:
        rows.append((e['id'], (e.get('name') or '')[:40], d, mx, e.get('dateLabel') or ''))
        e['date'] = mx
print('千秋楽を直すエントリ %d件' % len(rows))
for i, n, d, mx, lab in rows:
    print('  id%-5s %s | %s → %s' % (i, n, d, mx))
with io.open('tmp/evdate_label_todo_0912.txt', 'w', encoding='utf-8') as f:
    f.write('# 千秋楽(date)だけ直した。日付の欄(dateLabel)は未修正＝夜に1件ずつ見る（終わった公演の日は入れない決まり）\n')
    for i, n, d, mx, lab in rows:
        f.write('id%s | %s | date %s→%s | 今の日付の欄: %s\n' % (i, n, d, mx, lab))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
