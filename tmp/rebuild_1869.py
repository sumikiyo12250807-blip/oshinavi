# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, 'tools')
from build_pia_entries import build
import build_pia_entries as bpe

cand = {'newid': 1869, 'artist': '古澤巖',
        'urls': ['https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669275']}
ne = build(cand)
if ne is None:
    sys.stderr.write('BUILD None (0枠)\n')
else:
    sys.stderr.write('name=' + str(ne.get('name')) + '\n')
    sys.stderr.write('venue=' + repr(ne.get('venue')) + ' pref=' + str(ne.get('prefecture')) + ' date=' + str(ne.get('date')) + '\n')
    for t in ne['tickets']:
        sys.stderr.write('  type=' + repr(t.get('type')) + ' start=' + str(t.get('startDate')) + ' end=' + str(t.get('date')) + '\n')
    json.dump(ne, open('tmp/rebuild_1869.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if bpe._DROPPED:
    sys.stderr.write('DROPPED: ' + str(bpe._DROPPED) + '\n')
