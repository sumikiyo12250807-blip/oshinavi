# -*- coding: utf-8 -*-
"""スキップされた候補のカード状態をそのまま出す（読むだけ）。"""
import io, json, sys, time
sys.path.insert(0, 'tools')
import build_pia_entries as B
sys.stdout.reconfigure(encoding='utf-8')
cands = json.load(io.open('tmp/x0921/audit_fill_cands.json', encoding='utf-8'))
want = set(int(x) for x in sys.argv[1].split(',')) if len(sys.argv) > 1 else None
out = io.open('tmp/x0921/audit_fill_probe.txt', 'w', encoding='utf-8')
for c in cands:
    if want and c['newid'] not in want:
        continue
    u = c['urls'][0]
    h = B.fetch(u)
    cards = B.parse_cards(h)
    out.write('## %s %s %s err=%s wpia=%s cards=%d\n' % (c['newid'], c['artist'][:30], u, B.is_error_page(h), B.wpia_only(h), len(cards)))
    for r in cards:
        out.write('   state=%s stt=%r when=%r perf=%s..%s venue=%s title=%s\n' % (
            r.get('state'), r.get('stt'), r.get('when'), r.get('perfdate'), r.get('perf_end'), r.get('venue'), (r.get('title') or '')[:50]))
    time.sleep(1.0)
out.close()
print('done')
