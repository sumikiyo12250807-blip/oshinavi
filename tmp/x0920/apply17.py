# -*- coding: utf-8 -*-
"""取り直した17件の枠を既存エントリに**足す**（2026-09-20 朝）。

🚨置き換えない＝足す。置き換えるとヒールと同じ「券種違いを丸ごと消す」事故になる
   （[[feedback_heal_flattens_ticket_types]]）。売り切れ・販売終了の印が付いた枠も残す。
🚨同じ（券種名・締切・飛び先）の枠は足さない。
書き戻しは tools/inject_tiget.py と同じ型（CRLFに直してから書く）。

使い方: python tmp/x0920/apply17.py        … 下見
        python tmp/x0920/apply17.py --apply
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
NL = '\r\n'

built = json.load(io.open('tmp/x0920/rebuilt17.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by_id = {e['id']: e for e in EVENTS}

added, skipped = [], []
for b in built:
    e = by_id.get(b['id'])
    if e is None:
        skipped.append((b['id'], 'エントリが無い'))
        continue
    have = {(t.get('type'), t.get('date'), t.get('url')) for t in (e.get('tickets') or [])}
    for t in (b.get('tickets') or []):
        k = (t.get('type'), t.get('date'), t.get('url'))
        if k in have:
            skipped.append((b['id'], '既にある: ' + (t.get('type') or '')[:40]))
            continue
        if (t.get('date') or '') < TODAY and not t.get('soldout'):
            skipped.append((b['id'], '締切済み: ' + (t.get('type') or '')[:40]))
            continue
        have.add(k)
        added.append((b['id'], e.get('artist'), t))
        if APPLY:
            e.setdefault('tickets', []).append(t)

print('=== 取り直し17件の足し込み（today=%s）===' % TODAY)
print('足す %d枠 / 足さない %d枠' % (len(added), len(skipped)))
for i, n, t in added:
    print('  ＋ id%s %s ｜ %s' % (i, (n or '')[:26], t.get('type')))
for i, why in skipped:
    print('  − id%s %s' % (i, why))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_alive17', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
print('\nCRCRLF %d / 素のLF %d （どちらも0が正）'
      % (raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('書き込み完了（バックアップ index.html.bak_0920_alive17）')
