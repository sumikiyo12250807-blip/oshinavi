# -*- coding: utf-8 -*-
"""カード共通リンクのフォールバックに tiget が入っていない穴が、実害になっているか数える。

index.html の実物（539568行あたり）＝
  t.url || (ev.links && (rakuten || pia || eplus || lawson || fany || yoshimoto || tvasahi || shochiku || official))
＝**tiget を見ていない**。だから「ticket.url が空」で「links に tiget しか無い」エントリは
押しても行き先が無い。その件数を数える（[[feedback_check_existing_logic]]＝実物の条件式で数える）。
"""
import io, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TODAY = '2026-09-21'
# 実物のフォールバックの並び（tiget と zaiko が入っていない）
FALLBACK_NOW = ('rakuten', 'pia', 'eplus', 'lawson', 'fany',
                'yoshimoto', 'tvasahi', 'shochiku', 'official')

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


hole, byv = [], collections.Counter()
for e in ev:
    links = e.get('links') or {}
    common = next((links[k] for k in FALLBACK_NOW if links.get(k)), None)
    if common:
        continue                      # フォールバックが効く＝穴ではない
    miss = [t for t in (e.get('tickets') or []) if visible(t) and not (t.get('url') or '').strip()]
    if miss:
        hole.append((e, miss))
        byv[','.join(sorted(k for k, v in links.items() if v)) or '（リンク無し）'] += 1

out = io.open('tmp/x0921/link_fallback_hole.txt', 'w', encoding='utf-8')
out.write('=== 押しても行き先が無い枠（実物のフォールバックで判定）===\n')
out.write('エントリ %d件 / 枠 %d枠（全%d件中）\n\n'
          % (len(hole), sum(len(m) for _, m in hole), len(ev)))
out.write('--- 持っているリンクの種類別 ---\n')
for k, n in byv.most_common():
    out.write('  %-30s %4d件\n' % (k, n))
out.write('\n--- 明細（先頭40件）---\n')
for e, miss in hole[:40]:
    out.write('id%-6s %-10s %-32s 公演%s 枠%d\n'
              % (e['id'], e.get('genre'), (e.get('name') or e.get('artist') or '')[:32],
                 e.get('date'), len(miss)))
out.close()
print('穴 %d件 / %d枠 → tmp/x0921/link_fallback_hole.txt'
      % (len(hole), sum(len(m) for _, m in hole)))
