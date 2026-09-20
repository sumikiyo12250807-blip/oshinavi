# -*- coding: utf-8 -*-
"""🚨本当に飛び先が無いエントリを数える。
表示側は `t.url || カード共通リンク(ev.links の 楽天→ぴあ→e+→ローチケ→FANY→…)` の順で飛ぶので、
ticket.url が空でも links があれば買える。**両方とも無い枠**だけが「押しても行き先が無い」＝事故。
（index.html 536275行・536373行の実物のロジックを読んで確かめた＝[[feedback_check_existing_logic]]）
"""
import io, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
LINK_ORDER = ('rakuten', 'pia', 'eplus', 'lawson', 'fany', 'yoshimoto',
              'tvasahi', 'shochiku', 'official')

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

TODAY = '2026-09-21'


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


bad, badslots = [], 0
by_genre = collections.Counter()
for e in ev:
    common = next((v for k in LINK_ORDER for v in [(e.get('links') or {}).get(k)] if v), None)
    if common:
        continue
    miss = [t for t in (e.get('tickets') or []) if visible(t) and not (t.get('url') or '').strip()]
    if miss:
        bad.append((e, miss))
        badslots += len(miss)
        by_genre[e.get('genre')] += 1

out = io.open('tmp/x0921/no_dest_check.txt', 'w', encoding='utf-8')
out.write('=== 押しても行き先が無い枠（ticket.url も links も無い）===\n')
out.write('エントリ %d件 / 枠 %d枠（全%d件中）\n\n' % (len(bad), badslots, len(ev)))
for k, n in by_genre.most_common():
    out.write('  %-10s %4d件\n' % (k, n))
out.write('\n--- 明細（先頭60件）---\n')
for e, miss in bad[:60]:
    out.write('id%-6s %-10s %-34s 公演%s @ %s／枠%d\n'
              % (e['id'], e.get('genre'), (e.get('name') or e.get('artist') or '')[:34],
                 e.get('date'), (e.get('venue') or '')[:18], len(miss)))
out.close()
print('行き先が無いエントリ %d件 / %d枠 → tmp/x0921/no_dest_check.txt' % (len(bad), badslots))
