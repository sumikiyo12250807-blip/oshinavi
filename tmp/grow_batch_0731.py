# -*- coding: utf-8 -*-
"""監査で出た「本人名義の取りこぼし」8組を一括育成（2026-07-31・ユーザー「増やして」）。
tools/grow_from_audit.py と同じ流儀:
  上書き = tickets(ぴあ由来) / date(千秋楽は遅い方) / dateLabel / venue / prefecture
  守る   = artist / name / links / genre / verified と 非ぴあ枠
  安全弁 = 既存のぴあ枠が消える組は適用しない（--allow-drop が無い限り）＝報告に回す

  python tmp/grow_batch_0731.py            # ドライラン
  python tmp/grow_batch_0731.py --apply
"""
import os, re, sys, json, time, datetime, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_OUT = sys.__stdout__
ARGS = sys.argv[1:]
APPLY = '--apply' in ARGS
ALLOW_DROP = '--allow-drop' in ARGS

# id: (表示名, 追加するeventCd/eventBundleCd)
TARGETS = {
    3483: ('People In The Box', ['2622201', '2622297', '2622932']),
    3504: ('千住真理子（vl）', ['2626042', 'b2667789', '2614059', '2615212', 'b2667995']),
    3488: ('Little Glee Monster', ['2623939', '2629908', '2622085']),
    3486: ('みのや雅彦', ['2622641']),
    3485: ('眞名子新', ['2625611']),
    3489: ('Luciela', ['2626544']),
    3487: ('May’n', ['2628818']),
    3494: ('立川生九郎落語SHOW in太宰府', ['2614553']),
}


def say(m):
    _OUT.write(m + '\n'); _OUT.flush()


def cd_url(cd):
    key = 'eventBundleCd' if cd.startswith('b') else 'eventCd'
    return 'https://t.pia.jp/pia/event/event.do?%s=%s' % (key, cd)


def is_pia_ticket(t):
    u = t.get('url') or ''
    return (not u) or ('pia.jp' in u)


def perf_key(ty):
    m = re.search(r'[（(]([^（）()]*公演[^（）()]*)[）)]', ty or '')
    return m.group(1).strip() if m else (ty or '').strip()


s = importlib.util.spec_from_file_location('bpe', os.path.join(TOOLS, 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(s); s.loader.exec_module(bpe)

idx = os.path.join(ROOT, 'index.html')
h = open(idx, encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

L, built, skipped = [], {}, []
for eid, (nm, cds) in TARGETS.items():
    ev = byid.get(eid)
    if not ev:
        skipped.append((eid, nm, 'エントリ無し')); continue
    cur = ev.get('tickets') or []
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p:
        urls.append(p)
    for t in cur:
        if t.get('url') and 'pia' in t['url'] and t['url'] not in urls:
            urls.append(t['url'])
    add = [cd_url(c) for c in cds if cd_url(c) not in urls]
    urls += add

    L.append('=' * 70)
    L.append('id=%d %s   ぴあURL %d本（既存%d + 新規%d）' % (eid, nm, len(urls), len(urls) - len(add), len(add)))
    try:
        ne = bpe.build({'newid': eid, 'artist': ev.get('artist', ''), 'urls': urls})
    except Exception as ex:
        L.append('  🚨 build例外＝置換しない: %s %s' % (type(ex).__name__, str(ex)[:140]))
        skipped.append((eid, nm, 'build例外')); time.sleep(1.5); continue
    if ne is None:
        L.append('  🚨 買える枠ゼロで返った＝置換しない')
        skipped.append((eid, nm, '0枠')); time.sleep(1.5); continue

    kept = [t for t in cur if not is_pia_ticket(t)]
    newt = list(ne['tickets']) + kept
    nd = max([d for d in (ne.get('date'), ev.get('date')) if d])
    newk = {perf_key(t.get('type')) for t in ne['tickets']}
    lost = [t for t in cur if is_pia_ticket(t) and perf_key(t.get('type')) not in newk]

    L.append('  枠 %d → %d（非ぴあ据置 %d） / 千秋楽 %s → %s' % (len(cur), len(newt), len(kept), ev.get('date'), nd))
    L.append('  県 %s → %s' % (ev.get('prefecture'), ne.get('prefecture')))
    L.append('  会場 %s' % (ne.get('venue') or ''))
    L.append('  --- 作り直した枠 ---')
    for t in ne['tickets']:
        L.append('    %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))
    if lost:
        L.append('  🚨 消えるぴあ枠 %d件:' % len(lost))
        for t in lost:
            L.append('     × %s | date=%s' % (t.get('type'), t.get('date')))
        if not ALLOW_DROP:
            L.append('  → 枠が消えるので適用しない（要目視）')
            skipped.append((eid, nm, '消える枠あり')); time.sleep(1.5); continue

    built[eid] = {'tickets': newt, 'date': nd, 'dateLabel': ne.get('dateLabel'),
                  'venue': ne.get('venue'), 'prefecture': ne.get('prefecture'),
                  'n_before': len(cur), 'n_after': len(newt), 'name': nm}
    time.sleep(1.5)

L.append('=' * 70)
L.append('作り直せた %d 組 / 見送り %d 組' % (len(built), len(skipped)))
for eid, nm, why in skipped:
    L.append('  見送り id=%d %s  %s' % (eid, nm, why))
open('tmp/grow_batch_0731.txt', 'w', encoding='utf-8').write('\n'.join(L))
say('差分は tmp/grow_batch_0731.txt  （作り直せた %d 組 / 見送り %d 組）' % (len(built), len(skipped)))
for eid, v in built.items():
    say('  id=%d %s  枠 %d→%d' % (eid, v['name'], v['n_before'], v['n_after']))
for eid, nm, why in skipped:
    say('  見送り id=%d %s  %s' % (eid, nm, why))

if not APPLY:
    say('(ドライラン。適用は --apply)'); sys.exit(0)

for eid, v in built.items():
    e = byid[eid]
    e['tickets'] = v['tickets']
    e['date'] = v['date']
    for k in ('dateLabel', 'venue', 'prefecture'):
        if v[k]:
            e[k] = v[k]
    e['verifiedAt'] = datetime.date.today().isoformat()

bak = os.path.join(ROOT, 'index.html.bak_%s_growbatch' % datetime.date.today().strftime('%m%d'))
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
raw = open(idx, 'rb').read()
say('=== %d組 適用 (backup: %s) / 孤立LF=%d ===' % (len(built), os.path.basename(bak), raw.count(b'\n') - raw.count(b'\r\n')))
