# -*- coding: utf-8 -*-
"""安全弁が止めた分に取り直しを「足し算」で当てる（2026-09-15 朝）。heal_blocked_union_1805.py の今日版。
違い＝取り直しは今朝の --build の結果（tmp/heal_stale.json）を読む。対象は tmp/heal_blocked_hold_0915.txt
（安全弁が止めた30件から 4272 を外した29件＝4272 は取り直しにも「9/13 12:00発売」が出る＝ぴあは「後日販売」なので手で直す）。
  ・取り直しの枠は全部入れる（飛び先が空なら、置き換える元の枠の飛び先を引き継ぐ）
  ・元の枠は「取り直しのどれかに置き換えられた」ものだけ外す。置き換え＝
      ① 券種の基底名が同じで、売り場の番号が同じ／どちらかの飛び先が空／元が「M/D発売」の古い形
      ② 元に無かった【…】の札が付いただけ（売り場の番号と公演が同じ）
  ・それ以外の元の枠は全部そのまま残す＝画面から消える枠は出ない
  ・売り切れの印付きの元の枠は、置き換えがあっても残す（取り直しは売り切れを拾わない）
使い方: python tmp/heal_blocked_union_0915.py [--apply] [--ids-file ファイル] [--built ファイル]
  既定＝--ids-file tmp/heal_blocked_hold_0915.txt --built tmp/heal_stale.json
  救済（heal_stale_deadlines --ids ... --build の結果）に使う時＝--ids-file tmp/rescue_ids_0915.txt --built tmp/heal_ids.json
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


IDS_FILE = _arg('--ids-file', 'tmp/heal_blocked_hold_0915.txt')
BUILT = _arg('--built', 'tmp/heal_stale.json')
ids = [int(x) for x in io.open(IDS_FILE, encoding='utf-8').read().split(',') if x.strip()]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
built = {o['id']: o for o in json.load(io.open(BUILT, encoding='utf-8')) if o.get('status') == 'convert'}
OLD_FORM = re.compile(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*発売\s*$')


def replaces(n, o):
    bn, bo = H.base_type(n.get('type')), H.base_type(o.get('type'))
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    if bn == bo and (un == uo or not n.get('url') or not o.get('url') or OLD_FORM.search(o.get('type') or '')):
        return True
    # ② は「元に無かった【…】の札が付いただけ」の書き替えに限る（【仙台大会】）。
    #    同じ売り場の番号でも【電子チケット】↔【紙チケット】、4次プリセール↔一般発売、poco先行↔一般発売は別の枠。
    strip = lambda s: re.sub(r'【[^】]*】', '', s)
    return bool(n.get('url') and o.get('url') and un == uo and '【' not in bo
                and strip(bn) == bo and H.perf_key(n.get('type')) == H.perf_key(o.get('type')))


def vis(ts):
    return sum(1 for t in ts if H.visible_slot(t, TODAY))


total = 0
for i in ids:
    e, o = by.get(i), built.get(i)
    if not e or not o:
        print('id%-5s 取り直し無し＝触らない' % i)
        continue
    old = e.get('tickets') or []
    new = [dict(t) for t in o['tickets']]
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
    # 取り直しの枠が、残す元の枠（売り切れの印付き）と同じ券種・同じ公演なら、取り直し側を入れない（二重を作らない）
    keep_keys = {(H.base_type(t.get('type')), H._url_id(t.get('url'))) for t in kept if t.get('soldout')}
    new = [n for n in new if (H.base_type(n.get('type')), H._url_id(n.get('url'))) not in keep_keys]
    merged = new + kept
    ko = {H.slot_key(t) for t in merged if H.visible_slot(t, TODAY)}
    lost = [t for t in old if H.visible_slot(t, TODAY) and H.slot_key(t) not in ko
            and not any(replaces(n, t) for n in new)]
    e['tickets'] = merged
    total += 1
    print('id%-5s %s ｜出る枠 %d→%d（取り直し%d・置き換え%d・残す%d）%s' % (
        i, (e.get('name') or '')[:24], vis(old), vis(merged), len(new), len(gone), len(kept),
        '  🚨消える枠 %d' % len(lost) if lost else ''))
    for t in gone:
        if H.visible_slot(t, TODAY):
            cand = [x for x in new if replaces(x, t)]
            if cand:
                print('     置換 %s → %s ｜%s' % (t.get('type'), cand[0].get('type'), H._url_id(cand[0].get('url'))))
print('\n%d件' % total)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
