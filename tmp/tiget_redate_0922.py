# -*- coding: utf-8 -*-
"""延期・日程変更になったTIGETの2件を実ページから組み直し、公演日・会場・県・枠を差し替える。
  id13988 CREAM presents ＝ tiget 512890（台風で11/2に延期・POWER 8）
  id14033 注年時代 vol.8 ＝ tiget 519800（10/27 新宿永谷ホール）
既定は下見。--apply で index.html に書く（名前・ジャンル・出演者は触らない）。
"""
import datetime, importlib.util, io, json, re, sys

sys.path.insert(0, 'tools')
_prev = sys.stdout


_KEEP = []


def _load(path, name):
    # heal_tiget.py と同じ＝読み込んだ道具が差し替えた stdout を捨てずに持っておき、元に戻す
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TH = _load('tools/tiget_harvest.py', 'th')
BT = _load('tools/build_tiget_entries.py', 'bt')
sys.stdout = _KEEP[-1]

PAIRS = {13988: '512890', 14033: '519800'}
TODAY = datetime.date.today().isoformat()
KEYS = ('date', 'dateLabel', 'venue', 'prefecture', 'tickets')

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

changed = 0
for oid, eid in PAIRS.items():
    d = TH.parse_event(TH.fetch(f'https://tiget.net/events/{eid}'), eid)
    d['cats'] = ['81']
    d['list'] = {}
    built, why = BT.build(d, TODAY)
    e = by[oid]
    print('■ id%d %s' % (oid, e.get('name')))
    if not built:
        print('   組み直し空＝触らない:', why)
        continue
    for k in KEYS:
        if k == 'tickets':
            print('   枠 %d → %d' % (len(e.get('tickets') or []), len(built['tickets'])))
            for t in built['tickets']:
                print('      +', t.get('type'), '| start', t.get('startDate'), 'end', t.get('date'),
                      ''.join(x[0] for x in ('soldout', 'saleEnded', 'saleEndUnknown') if t.get(x)))
        else:
            print('   %s: %s → %s' % (k, e.get(k), built.get(k)))
    if '--apply' in sys.argv:
        for k in KEYS:
            if k in built:
                e[k] = built[k]
        changed += 1

if '--apply' in sys.argv and changed:
    # heal_tiget.py と同じ書き戻し（改行コードを保つ）
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
    print('書き込み完了 %d件' % changed)
