# -*- coding: utf-8 -*-
"""指定idのエントリを、登録済みのぴあURLから作り直す（reconcileのMISSING枠取り込み）。
grow_from_audit.py の置換ロジック（非ぴあ枠は据置・千秋楽/会場/県も更新）をそのまま使う。
  python tmp/regrow_0805.py 2744,3449          # ドライラン
  python tmp/regrow_0805.py 2744,3449 --apply  # 適用
"""
import datetime, importlib.util, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, fname))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


gfa = _load('gfa', 'grow_from_audit.py')
bpe = _load('bpe', 'build_pia_entries.py')

ids = [int(x) for x in sys.argv[1].split(',') if x.strip()]
apply_ = '--apply' in sys.argv

idx = os.path.join(ROOT, 'index.html')
h = open(idx, encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

built = {}
for i in ids:
    ev = byid[i]
    cur = ev.get('tickets') or []
    urls = gfa.pia_urls(ev)
    print('=' * 70)
    print('id=%d %s  ぴあURL %d本' % (i, ev.get('artist'), len(urls)))
    if not urls:
        print('  ぴあURL無し＝対象外')
        continue
    ne = bpe.build({'newid': i, 'artist': ev.get('artist', ''), 'urls': urls})
    if ne is None:
        print('  買える枠ゼロで返却＝置換しない')
        continue
    kept = [x for x in cur if not gfa.is_pia_ticket(x)]
    newt = gfa.merge_tickets(ne['tickets'], cur)
    nd = gfa.pick_date(ne.get('date'), ev.get('date'), kept)
    print('  枠 %d → %d（非ぴあ据置 %d）' % (len(cur), len(newt), len(kept)))
    print('  千秋楽 %s → %s' % (ev.get('date'), nd))
    print('  県 %s → %s' % (ev.get('prefecture'), ne.get('prefecture')))
    print('  日付表記 %s' % (ev.get('dateLabel') or ''))
    print('     →     %s' % (ne.get('dateLabel') or ''))
    print('  --- 今の枠 ---')
    for x in cur:
        print('    %s | date=%s start=%s' % (x.get('type'), x.get('date'), x.get('startDate')))
    print('  --- 作り直した枠 ---')
    for x in newt:
        print('    %s | date=%s start=%s' % (x.get('type'), x.get('date'), x.get('startDate')))
    lost = gfa.lost_pia_slots(ne['tickets'], cur)
    if lost:
        print('  消えるぴあ枠 %d件' % len(lost))
        for x in lost:
            print('      x %s | date=%s' % (x.get('type'), x.get('date')))
    built[i] = {'tickets': newt, 'date': nd, 'dateLabel': ne.get('dateLabel'),
                'venue': ne.get('venue'), 'prefecture': ne.get('prefecture')}

if apply_ and built:
    for i, v in built.items():
        e = byid[i]
        e['tickets'] = v['tickets']
        e['date'] = v['date']
        if v['dateLabel']:
            e['dateLabel'] = v['dateLabel']
        if v['venue']:
            e['venue'] = v['venue']
        if v['prefecture']:
            e['prefecture'] = v['prefecture']
        e['verifiedAt'] = datetime.date.today().isoformat()
    bak = os.path.join(ROOT, 'index.html.bak_%s_regrow' % datetime.date.today().strftime('%m%d'))
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    raw = open(idx, 'rb').read()
    stray = raw.count(b'\n') - raw.count(b'\r\n')
    print('=== %d件 適用 (backup: %s) / 孤立LF=%d ===' % (len(built), os.path.basename(bak), stray))
else:
    print('=== 表示のみ。適用は --apply ===')
