# -*- coding: utf-8 -*-
"""e+が売り手の枠を、e+実ページの文言で soldout / saleEnded に打ち分ける（枠単位）。
判定は必ず ticket.url のドメイン＝e+ の枠だけ（feedback_saleended_vs_soldout の罠2回目対策）。

  python tmp/mark_soldout_eplus_0815.py            # 判定だけ（dry-run）
  python tmp/mark_soldout_eplus_0815.py --apply    # index.html に適用

根拠は tmp/eplus_probe_out.txt（tmp/eplus_probe.py が実ページから落としたもの）。
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv

# --- probe出力を URL -> {statuses:[...], soldout:bool, alive:bool} に畳む ---
blocks = open('tmp/eplus_probe_out.txt', encoding='utf-8').read().split('=' * 78)
info = {}
for b in blocks:
    lines = [l for l in b.splitlines() if l.strip()]
    if not lines:
        continue
    url = lines[0].strip()
    if not url.startswith('http'):
        continue
    sts = re.findall(r'^\s+\[([^\]]+)\]', b, re.M)
    if not sts and '[取得失敗]' in b:
        info[url] = {'fetch_fail': True}
        continue
    info[url] = {
        'sts': sts,
        'soldout': any('予定枚数終了' in s or '完売' in s or '売切' in s for s in sts),
        'alive': any(s in ('受付中', '受付前') for s in sts),
        'fetch_fail': False,
    }

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

plan = []
for e in EVENTS:
    for i, t in enumerate(e.get('tickets') or []):
        u = t.get('url') or ''
        if 'eplus.jp' not in u or u not in info:
            continue
        d = info[u]
        if d.get('fetch_fail'):
            continue
        if d['alive']:
            continue                      # まだ買える窓がある＝触らない
        if (t.get('date') or '') < TODAY:
            continue                      # すでに画面から消えている枠は対象外
        want_soldout = d['soldout']
        cur_soldout = bool(t.get('soldout'))
        cur_ended = bool(t.get('saleEnded'))
        if want_soldout and cur_soldout and not cur_ended:
            continue
        if (not want_soldout) and cur_ended:
            continue
        plan.append((e['id'], e['name'], i, t.get('type'), want_soldout, cur_soldout, cur_ended))

print('=== e+枠の打ち分け %d枠 ===' % len(plan))
for eid, name, i, ty, want, cs, ce in plan:
    lbl = '予定枚数終了' if want else '販売終了'
    print('  id%-5d %-30s t%-2d %-46s -> %s' % (eid, name[:30], i, (ty or '')[:46], lbl))

if APPLY:
    byid = {e['id']: e for e in EVENTS}
    for eid, name, i, ty, want, cs, ce in plan:
        t = byid[eid]['tickets'][i]
        if want:
            t['soldout'] = True
            t.setdefault('soldoutSince', TODAY)
            t.pop('saleEnded', None)
            t.pop('saleEndedSince', None)
        else:
            t['soldout'] = True
            t.setdefault('soldoutSince', TODAY)
            t['saleEnded'] = True
            t.setdefault('saleEndedSince', TODAY)
    bak = 'index.html.bak_%s_eplus_soldout' % datetime.date.today().strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('\n適用しました (backup: %s)' % bak)
