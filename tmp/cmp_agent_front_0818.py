# -*- coding: utf-8 -*-
"""前半エージェント（id4489-4513）の独立再導出値と登録値を突き合わせる。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

AGENT_N = {
    4489: 2, 4490: 5, 4491: 1, 4492: 1, 4493: 1, 4494: 1, 4495: 1, 4496: 2,
    4497: 1, 4498: 3, 4499: 1, 4500: 5, 4501: 2, 4502: 2, 4503: 1, 4504: 1,
    4505: 1, 4506: 1, 4507: 2, 4508: 1, 4509: 1, 4510: 1, 4511: 2, 4512: 1,
    4513: 1,
}
AGENT_LAST = {
    4489: '2026-11-25', 4490: '2026-11-11', 4491: '2027-01-30', 4492: '2026-12-20',
    4493: '2027-05-21', 4494: '2026-11-21', 4495: '2026-11-28', 4496: '2026-11-23',
    4497: '2026-11-11', 4498: '2026-11-06', 4499: '2027-07-24', 4500: '2027-02-26',
    4501: '2026-12-09', 4502: '2027-01-14', 4503: '2026-11-07', 4504: '2026-12-09',
    4505: '2026-12-08', 4506: '2026-10-30', 4507: '2026-12-18', 4508: '2026-10-25',
    4509: '2026-11-28', 4510: '2026-10-10', 4511: '2026-10-03', 4512: '2026-11-02',
    4513: '2026-11-03',
}

raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S).group(1))
by_id = {e['id']: e for e in EVENTS}

ng = 0
print('%-6s %-22s %5s %5s %-12s %-12s' % ('id', '公演名', '登録', 'agent', 'ev.date', 'agent千秋楽'))
for i in sorted(AGENT_N):
    e = by_id.get(i)
    if not e:
        print('%-6d MISSING' % i); ng += 1; continue
    n = len([t for t in (e.get('tickets') or []) if not t.get('soldout')])
    mark = '' if n == AGENT_N[i] else '  🚨枠数'
    dmark = '' if e.get('date') == AGENT_LAST[i] else '  ⚠️千秋楽'
    if mark or dmark:
        ng += 1
    print('%-6d %-22s %5d %5d %-12s %-12s%s%s' % (
        i, (e.get('artist') or '')[:20], n, AGENT_N[i],
        e.get('date'), AGENT_LAST[i], mark, dmark))
print()
print('=== 不一致 %d件 / 25件 ===' % ng)
