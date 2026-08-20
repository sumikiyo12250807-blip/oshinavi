# -*- coding: utf-8 -*-
"""検証エージェントが独立に数えた「買える枠数」と登録枠数を突き合わせる。
AGENT_N は agent の報告をそのまま写す（こちらの値は agent に見せていない）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# 後半エージェント（id4514-4538）の報告値
AGENT_N = {
    4514: 2, 4515: 9, 4516: 2, 4517: 4, 4518: 2, 4519: 3, 4520: 1, 4521: 1,
    4522: 2, 4523: 4, 4524: 1, 4525: 2, 4526: 1, 4527: 3, 4528: 1, 4529: 1,
    4530: 1, 4531: 2, 4532: 1, 4533: 1, 4534: 2, 4535: 2, 4536: 1, 4537: 3,
    4538: 7,
}
# agent が読んだ千秋楽（ツアー全体の終端）
AGENT_LAST = {
    4514: '2026-12-04', 4515: '2026-11-23', 4516: '2026-11-29', 4517: '2026-12-13',
    4518: '2026-10-10', 4519: '2026-10-24', 4520: '2026-10-04', 4521: '2026-11-01',
    4522: '2026-11-10', 4523: '2026-12-19', 4524: '2026-11-19', 4525: '2026-12-24',
    4526: '2026-11-08', 4527: '2026-11-03', 4528: '2026-11-24', 4529: '2026-12-09',
    4530: '2026-11-28', 4531: '2027-01-17', 4532: '2026-10-24', 4533: '2026-11-27',
    4534: '2026-10-01', 4535: '2026-12-05', 4536: '2026-12-19', 4537: '2026-12-09',
    4538: '2026-09-19',
}

raw = io.open('index.html', 'r', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n', raw, re.S).group(1))
by_id = {e['id']: e for e in EVENTS}

print('%-6s %-24s %6s %6s %-12s %-12s' % ('id', '公演名', '登録枠', 'agent', 'ev.date', 'agent千秋楽'))
for i in sorted(AGENT_N):
    e = by_id.get(i)
    if not e:
        print('%-6d MISSING' % i); continue
    n = len([t for t in (e.get('tickets') or []) if not t.get('soldout')])
    mark = '' if n == AGENT_N[i] else '  🚨枠数'
    dmark = '' if e.get('date') == AGENT_LAST[i] else '  ⚠️千秋楽'
    print('%-6d %-24s %6d %6d %-12s %-12s%s%s' % (
        i, (e.get('artist') or '')[:22], n, AGENT_N[i],
        e.get('date'), AGENT_LAST[i], mark, dmark))
