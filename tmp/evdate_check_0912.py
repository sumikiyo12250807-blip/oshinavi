# -*- coding: utf-8 -*-
"""枠の公演日（券種名の「（… M/D公演）」）がエントリの千秋楽（date）より後になっているエントリを探す（読むだけ）。
refresh_deadlines は枠しか書き換えないので、同じまとめページの「後の回」を足すと千秋楽が古いまま残る
＝翌朝「公演が終わった」として削除候補に出る／画面から消える（reconcile の QC-EVDATE と同じ型）。
2026-09-12 昼に 7130『ホーム スイート ホーム』舞台挨拶（千秋楽9/12のまま9/20の回を足した）で見つけた。
使い方: python tmp/evdate_check_0912.py
出力: tmp/evdate_ids_0912.txt（直す候補のid）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def show_dates(ty):
    m = re.search(r'（([^（）]*)公演）', ty or '')
    out, y = [], 2026
    if not m:
        return out
    for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', m.group(1)):
        if r9:
            y = 2027
        out.append('%04d-%02d-%02d' % (y, int(mo), int(dd)))
    return out


hits = []
for e in ev:
    d = e.get('date') or ''
    mx = max((x for t in (e.get('tickets') or []) for x in show_dates(t.get('type'))), default='')
    if mx and mx > d:
        hits.append((e['id'], (e.get('name') or '')[:40], d, mx, e.get('dateLabel') or ''))
print('枠の公演日が千秋楽より後のエントリ %d件' % len(hits))
for i, n, d, mx, lab in hits:
    print('  id%-5s %s | 千秋楽 %s < 枠の公演日 %s | %s' % (i, n, d, mx, lab[:50]))
io.open('tmp/evdate_ids_0912.txt', 'w', encoding='utf-8').write(','.join(str(h[0]) for h in hits))
