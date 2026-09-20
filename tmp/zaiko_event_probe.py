# -*- coding: utf-8 -*-
"""ZAIKOの個別イベントページの props.event を掘る＝公演日・会場・券種・受付期間・売り状態。"""
import html as H, io, json, re, sys

src = sys.argv[1] if len(sys.argv) > 1 else 'tmp/zaiko_event_akb.html'
h = io.open(src, encoding='utf-8', errors='replace').read()
d = json.loads(H.unescape(re.search(
    r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', h, re.S).group(1)))
ev = (d.get('props') or {}).get('event') or {}
out = io.open('tmp/zaiko_event_probe.txt', 'w', encoding='utf-8')

out.write('=== event のキー ===\n%s\n\n' % sorted(ev.keys()))
out.write('=== 日付・会場・名前らしい値 ===\n')
for k in sorted(ev):
    v = ev[k]
    if isinstance(v, (dict, list)):
        continue
    if re.search(r'name|title|date|time|venue|place|open|start|end|status|url|slug|sale|pref',
                 k, re.I):
        out.write('  %-34s = %r\n' % (k, str(v)[:110]))

for k in ('venue', 'place', 'location', 'schedule', 'dates'):
    if isinstance(ev.get(k), dict):
        out.write('\n=== event.%s ===\n%s\n' % (k, json.dumps(ev[k], ensure_ascii=False, indent=1)[:900]))

tk = ev.get('tickets') or []
out.write('\n=== event.tickets %d件 / 1件目の全部 ===\n' % len(tk))
if tk:
    out.write(json.dumps(tk[0], ensure_ascii=False, indent=1)[:2600] + '\n')
    out.write('\n=== 全券種の要点 ===\n')
    for t in tk:
        pick = {k: v for k, v in t.items()
                if re.search(r'name|title|price|sale|lottery|status|start|end|date|sold|stock',
                             k, re.I) and not isinstance(v, (dict, list))}
        out.write('  %s\n' % json.dumps(pick, ensure_ascii=False)[:340])
out.close()
print('wrote tmp/zaiko_event_probe.txt  tickets=%d' % len(tk))
