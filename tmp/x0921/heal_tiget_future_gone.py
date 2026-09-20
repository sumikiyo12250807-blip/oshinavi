# -*- coding: utf-8 -*-
"""TIGETヒールで消えた枠のうち、**公演日が今日以降のもの**だけを抜く。
券種名の「（県 M/D公演）」「（県 M/D HH:MM公演）」から公演日を読む。
公演が終わった回が消えるのは正常（DELETE_GATE 1.）。今日以降が消えていたら手当てが要る。
"""
import datetime, io, json, re, subprocess, sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TODAY = datetime.date.today()
Y = TODAY.year


def events(text):
    return {e['id']: e for e in json.loads(
        re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


def show_date(t):
    """券種名から公演日を読む。R9年表記は翌年。読めなければ None。"""
    s = t.get('type') or ''
    m = re.search(r'(R(\d)年\s*)?(\d{1,2})/(\d{1,2})(?:\s*\d{1,2}:\d{2})?(?:〜[\d/]+)?公演', s)
    if not m:
        return None
    y = (2018 + int(m.group(2))) if m.group(2) else Y
    try:
        return datetime.date(y, int(m.group(3)), int(m.group(4)))
    except ValueError:
        return None


head = events(subprocess.run(['git', 'show', 'HEAD:index.html'],
                             capture_output=True).stdout.decode('utf-8'))
now = events(io.open('index.html', encoding='utf-8', newline='').read())

td = TODAY.isoformat()
out = io.open('tmp/x0921/heal_tiget_future_gone.txt', 'w', encoding='utf-8')
future, past, unknown = [], 0, []
for i, e in sorted(head.items()):
    n = now.get(i)
    if n is None:
        continue
    v_old = [t for t in (e.get('tickets') or []) if H.visible_slot(t, td)]
    kn = {H.slot_key(t) for t in (n.get('tickets') or []) if H.visible_slot(t, td)}
    for t in v_old:
        if H.slot_key(t) in kn:
            continue
        d = show_date(t)
        if d is None:
            unknown.append((i, e, t))
        elif d >= TODAY:
            future.append((i, e, t, d))
        else:
            past += 1

out.write('=== ヒールで消えた枠の内訳（today=%s）===\n' % td)
out.write('公演が終わっていた枠 %d枠（正常）\n' % past)
out.write('🚨公演が今日以降なのに消えた枠 %d枠\n' % len(future))
out.write('公演日が読めなかった枠 %d枠\n\n' % len(unknown))
out.write('--- 🚨今日以降なのに消えた ---\n')
for i, e, t, d in sorted(future, key=lambda x: x[3]):
    out.write('id%-6s 公演%s %-30s\n    %s%s\n    %s\n'
              % (i, d.isoformat(), (e.get('name') or '')[:30], t.get('type'),
                 '（売り切れ印つき）' if t.get('soldout') else '', t.get('url') or ''))
out.write('\n--- 公演日が読めなかった ---\n')
for i, e, t in unknown[:20]:
    out.write('id%-6s %-30s %s\n' % (i, (e.get('name') or '')[:30], t.get('type')))
out.close()
print('過去%d枠 / 🚨今日以降%d枠 / 読めない%d枠 → tmp/x0921/heal_tiget_future_gone.txt'
      % (past, len(future), len(unknown)))
