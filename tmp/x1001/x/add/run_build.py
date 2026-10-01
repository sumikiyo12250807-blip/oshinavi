# -*- coding: utf-8 -*-
"""build_in.json を build_pia_entries.build に通して built.json に保存し、枠を表示する（書き込みは tmp だけ）"""
import io, json, sys
sys.path.insert(0, 'tools')
import build_pia_entries as B
sys.stdout.reconfigure(encoding='utf-8')
cands = json.load(io.open('tmp/x1001/x/add/build_in.json', encoding='utf-8'))
out = []
for c in cands:
    e = B.build(c)
    print('\n=== %s %s → %s' % (c['newid'], c['artist'], 'OK' if e else 'skip'))
    if e:
        out.append(e)
        print('   %s | %s | pia=%s' % (e.get('venue'), e.get('dateLabel'), (e.get('links') or {}).get('pia')))
        for t in e.get('tickets') or []:
            print('    %s | sd=%s d=%s | %s' % (t.get('type'), t.get('startDate'), t.get('date'), t.get('url') or ''))
print('\nDROPPED', B._DROPPED)
json.dump(out, io.open('tmp/x1001/x/add/built.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
