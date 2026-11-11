# -*- coding: utf-8 -*-
"""チケットペイ由来カードの枠を**実ページから作り直して差し替える**（heal_tiget.py と同じ形・2026-11-12 新設）。

  python tools/heal_ticketpay.py               … gate_ticketpay_slots のレポートで食い違った id を下見
  python tools/heal_ticketpay.py --ids 1,2     … id 指定で下見
  python tools/heal_ticketpay.py --apply       … 書き込む（そのあと gate_ticketpay_slots.py --ids で 0 を確かめる）
  python tools/heal_ticketpay.py --selftest

## 作り直し方
番人と**同じ関数**（ticketpay_harvest.parse_event → build_ticketpay_entries.build）で枠を作る＝当てた後に番人を回せば 0。

## 守ること
- 🚨作り直しが空（出す側・公演が過去・読めない札）なら触らない＝消さない。件数を報告に出す
- 読めなかった（非公開・404）も触らない＝報告（消すかは DELETE_GATE.md の手順で人が決める）
- チケットペイ以外の売り場の枠（ぴあ・楽天等）は残す＝チケットペイの枠だけ差し替える
- id・ジャンル・名前・会場は触らない
- カードが1つのチケットペイページだけでできていて、作り直したカードの日付が違えば date と dateLabel を合わせる
  （主催者が公演日を変えた時＝TIGET 11/5 の学び）。他の売り場の枠があるカードは日付を触らない（報告だけ）
- 出演者の欄は「公演名のまま（手直ししていない）」時だけ、作り直しで読めた出演者に差し替える
"""
import argparse
import datetime
import importlib.util
import io
import json
import re
import sys
import time

_KEEP = []


def _load(path, name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TH = _load('tools/ticketpay_harvest.py', 'tph')
BT = _load('tools/build_ticketpay_entries.py', 'tpb')
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
URL_ID = re.compile(r'ticketpay\.jp/booking/\?event_id=(\d+)')
_n = lambda s: re.sub(r'[\s　]', '', s or '')


def heal_entry(e, pages):
    """pages＝{event_id: build の結果（dict か None）}。e を書き換えて、何をしたかの dict を返す。
    作り直しが1つでも空なら触らない（{'empty': True}）。"""
    tickets = e.get('tickets') or []
    if not pages or any(b is None for b in pages.values()):
        return {'empty': True}
    rebuilt = [t for b in pages.values() for t in b['tickets']]
    others = [t for t in tickets if 'ticketpay.jp' not in (t.get('url') or '')]
    old = [t for t in tickets if 'ticketpay.jp' in (t.get('url') or '')]
    e['tickets'] = others + rebuilt
    did = {'old': old, 'new': rebuilt}
    if len(pages) == 1:
        b = list(pages.values())[0]
        if b['date'] != e.get('date') or re.match(r'^[^\s（]*', b['dateLabel']).group(0) != \
                re.match(r'^[^\s（]*', e.get('dateLabel') or '').group(0):
            if others:
                did['date_report'] = (e.get('date'), b['date'])          # 他の売り場の枠があるカードは触らない
            else:
                did['date_fixed'] = (e.get('date'), e.get('dateLabel'), b['date'], b['dateLabel'])
                e['date'], e['dateLabel'] = b['date'], b['dateLabel']
        if b.get('artist') and b['artist'] != b['name'] and _n(e.get('artist')) == _n(e.get('name')):
            did['artist'] = (e.get('artist'), b['artist'])
            e['artist'] = b['artist']
        if _n(b['name']) != _n(e.get('name')):
            did['name_changed'] = (e.get('name'), b['name'])
    return did


def _selftest():
    tp = 'https://www.ticketpay.jp/booking/?event_id=9'
    e = {'id': 1, 'name': 'A', 'artist': 'A', 'date': '2026-12-01', 'dateLabel': '2026年12月1日(火)',
         'tickets': [{'type': 'old', 'date': '2026-11-30', 'url': tp},
                     {'type': 'ぴあ', 'date': '2026-11-29', 'url': 'https://t.pia.jp/x'}]}
    b = {'name': 'A', 'artist': '出演者B', 'date': '2026-12-02', 'dateLabel': '2026年12月2日(水) 19:00開演',
         'tickets': [{'type': 'new', 'date': '2026-11-30', 'url': tp, 'soldout': True}]}
    did = heal_entry(e, {'9': b})
    assert [t['type'] for t in e['tickets']] == ['ぴあ', 'new'], e['tickets']        # 他の売り場は残す
    assert e['date'] == '2026-12-01' and did.get('date_report'), did                    # 他の売り場があれば日付は触らない
    assert e['artist'] == '出演者B'
    e2 = {'id': 2, 'name': 'A', 'artist': '手直し', 'date': '2026-12-01', 'dateLabel': '2026年12月1日(火)',
          'tickets': [{'type': 'old', 'date': '2026-11-30', 'url': tp}]}
    did = heal_entry(e2, {'9': b})
    assert e2['date'] == '2026-12-02' and did.get('date_fixed') and e2['artist'] == '手直し', (e2, did)
    e3 = {'id': 3, 'name': 'A', 'tickets': [{'type': 'old', 'url': tp}]}
    assert heal_entry(e3, {'9': None}) == {'empty': True} and e3['tickets'][0]['type'] == 'old'   # 空なら触らない
    print('selftest OK（他の売り場の枠は残す・空なら触らない・日付は単独カードだけ・手直しした出演者は戻さない）')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--gate-report', default='tmp/gate_ticketpay_report.txt')
    ap.add_argument('--report', default='tmp/heal_ticketpay_report.txt')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    if a.ids:
        want = {int(x) for x in re.findall(r'\d+', a.ids)}
    else:
        want = {int(x) for x in re.findall(r'🚨[^\n]*? (\d+) event_id=',
                                            io.open(a.gate_report, encoding='utf-8').read())}
    src = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    # ページに札が無い型（公演日時を選ぶ型）は一覧の札を使う＝番人・組み立てと同じ物差し
    lists, _ = TH.harvest_lists(a.sleep) if want else ({}, {})
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== heal_ticketpay (today=%s) 対象%d件 apply=%s ===\n' % (a.today, len(want), a.apply))
    done, empty, err = 0, [], []
    for e in events:
        if e['id'] not in want:
            continue
        urls = sorted({x for t in (e.get('tickets') or []) + [{'url': (e.get('links') or {}).get('ticketpay')}]
                       for x in URL_ID.findall(t.get('url') or '')})
        pages, bad = {}, False
        for eid in urls:
            try:
                t, final = TH.fetch('%s/booking/?event_id=%s' % (TH.BASE, eid))
                if 'event_id=%s' % eid not in final:
                    raise ValueError('トップへ飛んだ（非公開・削除）')
                d = TH.parse_event(t, eid)
                li = lists.get(int(eid)) or {}
                d['cats'] = li.get('cats') or []
                d['list_status'] = li.get('list_status') or ''
                d['list_class'] = li.get('list_class') or ''
                pages[eid] = BT.build(d, a.today)[0]
            except Exception as ex:
                err.append((e['id'], eid, str(ex)[:80]))
                bad = True
            time.sleep(a.sleep)
        if bad:
            continue
        did = heal_entry(e, pages)
        if did.get('empty'):
            empty.append(e)
            continue
        done += 1
        rep.write('\n■ id=%s %s  チケットペイ枠 %d → %d\n' % (e['id'], (e.get('name') or '')[:40], len(did['old']), len(did['new'])))
        for t in did['old']:
            rep.write('    旧: %s | %s%s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else '',
                                              ' 販売終了' if t.get('saleEnded') else ''))
        for t in did['new']:
            rep.write('    新: %s | %s%s%s\n' % (t.get('type'), t.get('date'), ' 売切' if t.get('soldout') else '',
                                              ' 販売終了' if t.get('saleEnded') else ''))
        for k in ('date_fixed', 'date_report', 'artist', 'name_changed'):
            if did.get(k):
                rep.write('    %s: %s\n' % ({'date_fixed': 'カードの日付を直した', 'date_report': '⚠️カードの日付が違う（他の売り場あり・触らず）',
                                              'artist': '出演者', 'name_changed': '⚠️公演名が変わった（触らず）'}[k], did[k]))
    rep.write('\n--- 作り直しが空（触らなかった）---\n')
    for e in empty:
        rep.write('  id=%s %s\n' % (e['id'], (e.get('name') or '')[:40]))
    for i, eid, why in err:
        rep.write('❌ id=%s event_id=%s 読めなかった: %s\n' % (i, eid, why))
    rep.write('\n=== 差し替え %d / 空で触らず %d / 読めず %d ===\n' % (done, len(empty), len(err)))
    rep.close()
    sys.stderr.write('heal_ticketpay: healed=%d empty=%d fetcherr=%d apply=%s -> %s\n'
                     % (done, len(empty), len(err), a.apply, a.report))
    if not a.apply or not done:
        return
    nl = '\r\n' if '\r\n' in src else '\n'
    out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(out)


if __name__ == '__main__':
    main()
