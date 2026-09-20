# -*- coding: utf-8 -*-
"""番人のレポートから食い違いのidを機械で取り、そのエントリの枠を並べる。
あわせて**ticket.url が空の枠**（＝購入ボタンの飛び先が無い＝買えない）を全件数える。
🚨idは手で拾わない（[[feedback_no_fabricated_output]]／[[feedback_entry_name_with_id]]）。
"""
import io, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rep = io.open('tmp/gate_fany_report.txt', encoding='utf-8').read()
head, _, rest = rep.partition('=== 一覧から落ちた')
ng_ids = []
for m in re.finditer(r'^--- event/detail/(\d+)\s+id([0-9,]+)', head, re.M):
    ng_ids += [int(x) for x in m.group(2).split(',')]

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in ev}

out = io.open('tmp/x0921/fany_diff_read.txt', 'w', encoding='utf-8')
out.write('番人が鳴らしたid（機械抽出）= %s\n\n' % ng_ids)
for i in ng_ids:
    e = byid.get(i)
    if not e:
        out.write('id%s は今のindex.htmlに無い\n\n' % i)
        continue
    out.write('=== id%s %s @ %s（%s）公演%s\n'
              % (i, (e.get('name') or e.get('artist') or '')[:44], e.get('venue'),
                 e.get('prefecture'), e.get('date')))
    out.write('  links: %s\n' % {k: v for k, v in (e.get('links') or {}).items() if v})
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        who = ('FANY' if 'fany.lol' in u else 'ぴあ' if 'pia.jp' in u
               else 'e+' if 'eplus' in u else '楽天' if 'rakuten' in u
               else 'TIGET' if 'tiget' in u else ('🚨URL空' if not u else 'その他'))
        flags = ' '.join(k for k in ('soldout', 'saleEnded', 'presaleEnded', 'saleEndUnknown')
                         if t.get(k))
        out.write('  [%-6s] %s | date=%s %s\n' % (who, t.get('type'), t.get('date'), flags))
    out.write('\n')

# 全体＝url が空の枠を数える
empty = collections.Counter()
rows = []
for e in ev:
    for t in e.get('tickets') or []:
        if not (t.get('url') or '').strip():
            empty[e.get('genre')] += 1
            rows.append((e['id'], e.get('genre'), (e.get('name') or e.get('artist') or '')[:34],
                         t.get('type')))
out.write('=== 🚨ticket.url が空の枠（購入ボタンの飛び先が無い）= %d枠 / %dエントリ ===\n'
          % (len(rows), len({r[0] for r in rows})))
for k, n in empty.most_common():
    out.write('  %-10s %5d枠\n' % (k, n))
out.write('\n--- 先頭40枠 ---\n')
for r in rows[:40]:
    out.write('  id%-6s %-10s %-34s %s\n' % r)
out.close()
print('ng=%d件 / url空の枠=%d枠（%dエントリ）→ tmp/x0921/fany_diff_read.txt'
      % (len(ng_ids), len(rows), len({r[0] for r in rows})))
