# -*- coding: utf-8 -*-
"""別系統(pia_tickets.py)の実ページ値 ⇄ 登録値 の突合・改訂版。
v1の誤検知2型を修正:
 ・ぴあは「昼12:00 / 夜7:00」と書く（時刻の前に朝昼夜が入る）
 ・発売前の枠はバッジに発売日時だけ出し、締切は ticket.date が持つ（カウントダウン仕様）
比較は「発売日時(start)」と「締切日(end)」を分けて、実ページ側の窓ごとに集合で照合する。
"""
import re, io, json, sys, subprocess, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']

CACHE_F = 'tmp/indep_cache_0803.json'
cache = json.load(io.open(CACHE_F, encoding='utf-8')) if os.path.exists(CACHE_F) else {}

def fetch(u):
    if u in cache:
        return cache[u]
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', u, '--json'], capture_output=True)
    try:
        d = json.loads(r.stdout.decode('utf-8'))
    except Exception:
        d = [{'_error': (r.stdout + r.stderr).decode('utf-8', 'replace')[:200]}]
    cache[u] = d
    time.sleep(1.2)
    return d

DT = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:朝|昼|夜|夕|深夜)?\s*(\d{1,2}):(\d{2})')

def md(m):
    return '%d/%d' % (int(m.group(2)), int(m.group(3)))

def mdhm(m):
    return '%d/%d %d:%02d' % (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))

def real_window(w):
    """実ページの when → (start 'M/D H:MM'|None, end 'M/D'|None)"""
    ms = list(DT.finditer(w))
    if not ms:
        return None, None
    if '～' in w or '〜' in w:
        head = w.split('～')[0].split('〜')[0]
        if DT.search(head):
            return mdhm(ms[0]), (md(ms[1]) if len(ms) > 1 else None)
        return None, md(ms[0])
    if 'より発売' in w or '発売' in w:
        return mdhm(ms[0]), None
    return None, md(ms[0])

def reg_window(t):
    """登録ticket → (バッジの発売日時|None, ticket.dateのM/D)"""
    typ = t.get('type', '')
    m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})\s*(?:発売開始|発売予定|発売|販売開始|受付開始)\s*$', typ)
    start = '%d/%d %d:%02d' % tuple(int(x) for x in m.groups()) if m else None
    end_badge = re.search(r'〜\s*(\d{1,2})/(\d{1,2})(?:\s+\d{1,2}:\d{2})?\s*$', typ)
    dd = t.get('date') or ''
    dm = '%d/%d' % (int(dd[5:7]), int(dd[8:10])) if len(dd) == 10 else None
    return start, dm, (end_badge is not None)

BUY = ('受付中', '発売前', '販売期間中', '抽選受付', '先着')
ng = []
lines = []
for e in new:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p:
        urls.append(p)
    for t in e.get('tickets') or []:
        if t.get('url') and t['url'] not in urls:
            urls.append(t['url'])
    got, err = [], []
    for u in urls:
        d = fetch(u)
        if d and isinstance(d[0], dict) and d[0].get('_error'):
            err.append(d[0]['_error'])
            continue
        for c in d:
            if any(b in (c.get('state') or '') for b in BUY):
                k = (c.get('title'), c.get('when'), c.get('perfdate'), c.get('pref'))
                if k not in [g[0] for g in got]:
                    got.append((k, c))
    regs = e.get('tickets') or []
    msgs = []
    if err:
        msgs.append('取得エラー')
    if len(got) != len(regs):
        msgs.append('枠数 登録%d ⇄ 実%d' % (len(regs), len(got)))
    real = sorted(str(real_window(c.get('when') or '')) for _, c in got)
    reg = []
    for t in regs:
        s, dm, has_end = reg_window(t)
        # 発売前(バッジに発売日時)なら実は(start, end or None)。締切はticket.dateが持つ
        reg.append(str((s, dm if (has_end or s is None) else (dm if dm != (s.split(' ')[0] if s else None) else None))))
    reg = sorted(reg)
    if real != reg:
        msgs.append('日時 登録%s ⇄ 実%s' % (reg, real))
    if msgs:
        ng.append(e['id'])
        lines.append('\n❌ id%d %s' % (e['id'], e['name'][:34]))
        for m in msgs:
            lines.append('     ' + m)
        for _, c in got:
            lines.append('     [実] %s | %s | %s' % (c.get('state'), (c.get('title') or '')[:40], c.get('when')))
        for t in regs:
            lines.append('     [登] %s | date=%s start=%s' % (t.get('type', '')[:60], t.get('date'), t.get('startDate')))
    else:
        lines.append('✅ id%d %s | %d枠一致' % (e['id'], e['name'][:26], len(regs)))

json.dump(cache, io.open(CACHE_F, 'w', encoding='utf-8'), ensure_ascii=False)
print('\n'.join(lines))
print('\n=== 不一致 %d / %d件 %s ===' % (len(ng), len(new), ng))
