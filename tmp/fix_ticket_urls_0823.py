# -*- coding: utf-8 -*-
"""統合で足した枠のうち url が無いものに、その枠の売り場URLを刻む。

なぜ要るか（2026-08-23 発見）:
  build_pia_entries に複数URLを渡して再導出すると、2本目以降のURLから拾った枠にも
  ticket.url が付かない。エントリの links.pia（＝1本目＝古い公演のページ）に飛ぶので、
  「その枠を売っていないページ」に着地する＝買えない。reconcile が STALE で気づいた。
  [[feedback_dedup_badges_keeps_urls]]＝飛び先が違えば別の売り場。導線を消さない。
"""
import re, io, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

plans = json.load(io.open('tmp/merge_plan_0823.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def md_list(perf):
    """'2026/11/20(金)' や '2026/9/27(日) ～ 2026/10/25(日)' から M/D を全部取る"""
    return ['%d/%d' % (int(a), int(b)) for a, b in re.findall(r'\d{4}/(\d{1,2})/(\d{1,2})', perf or '')]


def pref_short(p):
    return re.sub(r'(都|道|府|県)$', '', p or '')


fixed = []
for p in plans:
    e = by.get(p['id'])
    if not e:
        continue
    main = (e.get('links') or {}).get('pia')
    for c in p['cand']:
        mds = md_list(c.get('perfdate'))
        pf = pref_short(c.get('pref'))
        cu = re.sub(r'^https?://[^/]+', 'https://t.pia.jp', c['url']).replace('/pia/event.do', '/pia/event/event.do')
        for t in e.get('tickets') or []:
            if t.get('url'):
                continue
            ty = t.get('type') or ''
            if pf and pf not in ty:
                continue
            if not any(md in ty for md in mds):
                continue
            fixed.append((p['id'], ty, cu))
            if APPLY:
                t['url'] = cu

print('url を刻む枠 %d件' % len(fixed))
for i, ty, u in fixed:
    print('  id%-5d %s → %s' % (i, ty, u))

if APPLY:
    io.open('index.html.bak_0823_ticketurl', 'w', encoding='utf-8').write(h)
    io.open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（見ただけ。適用は --apply）')
