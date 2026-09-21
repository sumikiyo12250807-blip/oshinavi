# -*- coding: utf-8 -*-
"""エージェントが挙げたZAIKOの二重登録11件（＋疑い3件）を、あたし自身で確かめる。
🚨名前が同じでも中身が別物のことが多い（TIGETで7件調べて0件だった＝NoGoDの5会場が
消えるところだった＝[[feedback_harvest_name_dedup_blindspot]]）。**畳む前に必ず中身を見る**。
"""
import io, json, re, sys, unicodedata

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SUSPECT = [20481, 20482, 20556, 20668, 20693, 20709, 20716, 20780, 20820, 20838, 20856]
MAYBE = [20564, 20757, 20875]


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in ev}

out = io.open('tmp/x0921/zaiko_dup_check.txt', 'w', encoding='utf-8')
for i in SUSPECT + MAYBE:
    z = byid.get(i)
    if not z:
        out.write('id%s は無い\n\n' % i)
        continue
    out.write('=== ZAIKO id%s %s\n    %s @ %s（%s）公演%s\n'
              % (i, (z.get('name') or '')[:46], (z.get('artist') or '')[:34],
                 z.get('venue'), z.get('prefecture'), z.get('date')))
    out.write('    %s\n' % (z.get('links') or {}).get('zaiko'))
    for t in z.get('tickets') or []:
        out.write('      枠: %s\n' % (t.get('type') or '')[:70])
    # 同じ名前・同じ公演日の既存を探す（ZAIKO以外）
    hits = []
    for e in ev:
        if e['id'] == i or (e.get('links') or {}).get('zaiko'):
            continue
        if e.get('date') != z.get('date'):
            continue
        if norm(e.get('name')) == norm(z.get('name')) or norm(e.get('artist')) == norm(z.get('artist')) \
           or norm(e.get('name')) == norm(z.get('artist')) or norm(e.get('artist')) == norm(z.get('name')):
            hits.append(e)
    if not hits:
        out.write('    → 同名×同日の既存は**無い**（畳む必要なし）\n\n')
        continue
    for e in hits:
        ls = {k: v for k, v in (e.get('links') or {}).items() if v}
        out.write('    ◆既存 id%s %s @ %s（%s）\n      売り場: %s\n'
                  % (e['id'], (e.get('name') or e.get('artist') or '')[:44],
                     e.get('venue'), e.get('prefecture'), list(ls)))
        for t in e.get('tickets') or []:
            out.write('        枠: %s\n' % (t.get('type') or '')[:70])
        # 会場が同じかどうかが決め手
        same_venue = norm(e.get('venue')) == norm(z.get('venue'))
        out.write('      会場一致=%s\n' % same_venue)
    out.write('\n')
out.close()
print('wrote tmp/x0921/zaiko_dup_check.txt')
