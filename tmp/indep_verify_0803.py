# -*- coding: utf-8 -*-
"""新着50件を【別系統ツール】tools/pia_tickets.py でゼロから取り直し、登録値と突合する。
build_pia_entries / reconcile_pia とは別実装なので、同じコード同士のアンカリングにならない。
memory: feedback_verify_independent_not_anchored / feedback_zero_error_pipeline
"""
import re, io, json, sys, subprocess, time, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']

def urls_of(e):
    out = []
    p = (e.get('links') or {}).get('pia')
    if p:
        out.append(p)
    for t in e.get('tickets') or []:
        u = t.get('url')
        if u and u not in out:
            out.append(u)
    return out

cache = {}
def fetch(u):
    if u in cache:
        return cache[u]
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', u, '--json'],
                       capture_output=True)
    try:
        d = json.loads(r.stdout.decode('utf-8'))
    except Exception:
        d = {'_error': r.stdout.decode('utf-8', 'replace')[:200] + r.stderr.decode('utf-8', 'replace')[:200]}
    cache[u] = d
    time.sleep(1.2)
    return d

DT = r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(\d{1,2}):(\d{2})'

def parse_when(w):
    """→ (start_str|None, end_str|None)  各 'M/D HH:MM'"""
    def s(m):
        return '%d/%d %d:%02d' % (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))
    ms = list(re.finditer(DT, w))
    if '～' in w or '〜' in w:
        if len(ms) >= 2:
            return s(ms[0]), s(ms[1])
        if len(ms) == 1:
            # 「～ 終了日時」だけ
            head = w.split('～')[0].split('〜')[0]
            return (s(ms[0]), None) if re.search(DT, head) else (None, s(ms[0]))
        return None, None
    if ms and 'より発売' in w:
        return s(ms[0]), None
    if len(ms) == 1:
        return None, s(ms[0])
    return None, None

def reg_when(t):
    """登録ticket.type の末尾から (start,end) を取り出す"""
    typ = t.get('type', '')
    m_end = re.search(r'〜\s*(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?\s*$', typ)
    m_sale = re.search(r'(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?\s*(?:発売開始|発売予定|発売|販売開始|受付開始|受付)\s*$', typ)
    def f(m):
        if not m:
            return None
        hh = m.group(3) or '0'
        mm = m.group(4) or '00'
        return '%d/%d %d:%s' % (int(m.group(1)), int(m.group(2)), int(hh), mm)
    return f(m_sale), f(m_end)

BUY = ('受付中', '発売前', '販売期間中', '抽選受付中', '先着受付中')
rows = []
for e in new:
    got = []
    err = []
    for u in urls_of(e):
        d = fetch(u)
        if isinstance(d, dict) and d.get('_error') is not None:
            err.append(d['_error'])
            continue
        for c in d:
            if any(b in (c.get('state') or '') for b in BUY):
                key = (c.get('title'), c.get('when'), c.get('perfdate'), c.get('pref'))
                if key not in [g['key'] for g in got]:
                    got.append({'key': key, **c})
    rows.append((e, got, err))

print('=== 別系統(pia_tickets.py)での独立再取得 ===')
ng = 0
for e, got, err in rows:
    regs = e.get('tickets') or []
    msgs = []
    if err:
        msgs.append('取得エラー %s' % err[:1])
    if len(got) != len(regs):
        msgs.append('枠数 登録%d ⇄ 実ページ%d' % (len(regs), len(got)))
    # 日時集合の突合
    gset = set()
    for c in got:
        st, en = parse_when(c.get('when') or '')
        gset.add((st, en))
    rset = set()
    for t in regs:
        st, en = reg_when(t)
        rset.add((st, en))
    if gset != rset:
        msgs.append('日時 登録%s ⇄ 実%s' % (sorted(map(str, rset)), sorted(map(str, gset))))
    if msgs:
        ng += 1
        print('\n❌ id%d %s' % (e['id'], e['name'][:34]))
        for m in msgs:
            print('    ', m)
        for c in got:
            print('     [実] %s | %s | %s' % (c.get('state'), c.get('title', '')[:38], c.get('when')))
        for t in regs:
            print('     [登] %s' % t.get('type', '')[:70])
    else:
        print('✅ id%d %s | %d枠一致' % (e['id'], e['name'][:26], len(regs)))

print('\n=== 不一致 %d / %d件 ===' % (ng, len(rows)))
