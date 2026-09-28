# -*- coding: utf-8 -*-
"""既存エントリへの足し込み（2026-09-28 朝・ぴあ発売前スイープ）。tmp/x0927/heal_union_merge.py と同じ「足し算」。
入力:
  ・tmp/x0928e/w/NONE.json（eventCd が登録済みの12件・pia_merge_in.json の target へ）
  ・tmp/x0928e/w/built_new.json のうち NAME_MERGE に挙げた newid（同じツアー／長期公演の別ページ）
やること:
  ・取り直しの枠は全部入れる。元の枠は「取り直しに置き換えられた」ものだけ外す（置き換え判定は heal_union_merge と同じ）
  ・足した枠の飛び先が空で、その売り場が target の links.pia と違うなら、候補URLを刻む（feedback_build_pia_multiurl_loses_ticket_url）
  ・ev.date は足した枠の公演が後ろなら伸ばす（千秋楽）
使い方: python tmp/x0928/merge_add.py [--apply]
"""
import datetime, io, json, re, sys
sys.path.insert(0, 'tools')
import heal_stale_deadlines as H
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
NAME_MERGE = {25251: 2338, 25252: 3471, 25253: 3471, 25284: 3406, 25270: 23644, 25255: 22537}

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
OLD_FORM = re.compile(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*発売\s*$')

jobs = []  # (target, cand_url, built_entry)
mi = {c['newid']: c for c in json.load(io.open('tmp/x0928e/w/NONE_in.json', encoding='utf-8'))}
for b in json.load(io.open('tmp/x0928e/w/NONE.json', encoding='utf-8')):
    c = mi[b['id']]
    jobs.append((c['target'], c['urls'][0], b))
for b in json.load(io.open('tmp/x0928e/w/built_new.json', encoding='utf-8')):
    if b['id'] in NAME_MERGE:
        jobs.append((NAME_MERGE[b['id']], (b.get('links') or {}).get('pia'), b))
missing_builds = [c['newid'] for c in mi.values() if c['newid'] not in {j[2]['id'] for j in jobs}]


def replaces(n, o):
    bn, bo = H.base_type(n.get('type')), H.base_type(o.get('type'))
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    if n.get('url') and o.get('url') and un != uo:
        return False   # 飛び先の売り場が違えば別の枠（feedback_dedup_badges_keeps_urls）
    if bn == bo and (un == uo or not n.get('url') or not o.get('url') or OLD_FORM.search(o.get('type') or '')):
        return True
    strip = lambda s: re.sub(r'【[^】]*】', '', s)
    return bool(n.get('url') and o.get('url') and un == uo and '【' not in bo
                and strip(bn) == bo and H.perf_key(n.get('type')) == H.perf_key(o.get('type')))


def vis(ts):
    return sum(1 for t in ts if H.visible_slot(t, TODAY))


added_total, touched = 0, []
for tid, curl, b in jobs:
    e = by.get(tid)
    if not e:
        print('id%s 無い＝触らない' % tid); continue
    lp = H._url_id((e.get('links') or {}).get('pia'))
    new = [dict(t) for t in b.get('tickets') or []]
    for n in new:
        if not n.get('url') and H._url_id(curl) != lp:
            n['url'] = curl
        # ぴあシートのページは券種名が「一般発売」になる＝通常券と同じ文言で並ぶ。ページ表題どおり「ぴあシート」と名乗らせる（id72 と同じ形）
        if 'ぴあシート' in (b.get('artist') or '') and (n.get('type') or '').startswith('一般発売（'):
            n['type'] = 'ぴあシート' + n['type'][len('一般発売'):]
    old = e.get('tickets') or []
    # まとめページと公演ページで同じ窓が二重に出る＝基底名と締切（または発売日）が同じで、飛び先だけ違う枠は足さない
    same = [n for n in new if any(n.get('url') and t.get('url') and H._url_id(n['url']) != H._url_id(t['url'])
                                  and H.base_type(n.get('type')) == H.base_type(t.get('type'))
                                  and (n.get('date') == t.get('date') or (n.get('startDate') and n.get('startDate') == t.get('startDate')))
                                  for t in old)]
    for n in same:
        print('     （既にある窓＝別URLで登録済み・足さない）%s' % n.get('type'))
    new = [n for n in new if n not in same]
    gone, kept = [], []
    for t in old:
        rep = [n for n in new if replaces(n, t)]
        if rep and not t.get('soldout'):
            for n in rep:
                if not n.get('url') and t.get('url'):
                    n['url'] = t['url']
                if not n.get('startDate') and t.get('startDate'):
                    n['startDate'] = t['startDate']
            gone.append(t)
        else:
            kept.append(t)
    merged = kept + new
    ko = {H.slot_key(t) for t in merged if H.visible_slot(t, TODAY)}
    lost = [t for t in old if H.visible_slot(t, TODAY) and H.slot_key(t) not in ko and not any(replaces(n, t) for n in new)]
    e['tickets'] = merged
    if b.get('date') and (e.get('date') or '') < b['date']:
        e['date'] = b['date']
    added = len(new) - len([t for t in gone])
    added_total += len(new)
    touched.append(tid)
    print('id%-5s %s ←(%s) %s ｜出る枠 %d→%d（取り直し%d・置き換え%d・残す%d）%s' % (
        tid, (e.get('name') or '')[:22], b['id'], H._url_id(curl), vis(old), vis(merged), len(new), len(gone), len(kept),
        '  🚨消える枠 %d' % len(lost) if lost else ''))
    for n in new:
        print('     + %s | date=%s start=%s url=%s' % (n.get('type'), n.get('date'), n.get('startDate'), n.get('url')))
    for t in gone:
        print('     置換 %s' % t.get('type'))
print('\n足し込み %d件（のべ）・枠 %d / id=%s' % (len(jobs), added_total, ','.join(str(i) for i in sorted(set(touched)))))
print('組み立て無し（skip）: %s' % missing_builds)
io.open('tmp/x0928e/w/merge_ids.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(set(touched))))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
