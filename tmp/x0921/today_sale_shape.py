# -*- coding: utf-8 -*-
"""「本日発売」の枠が、締切つきの形になっているかを数える（昼ヒールの前後で比べる）。
朝は「本日発売」だけ → 昼のヒールで「本日発売 〜M/D」に変わるのが正
（[[feedback_harvest_today_sale_enddate]]／SKILL.md 第2便）。
"""
import io, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TODAY = '2026-09-21'
tag = sys.argv[1] if len(sys.argv) > 1 else 'before'

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

start_today = []          # startDate == today の枠（＝本日発売）
for e in ev:
    for t in e.get('tickets') or []:
        if t.get('startDate') == TODAY:
            start_today.append((e['id'], e.get('genre'), t.get('type') or '', t.get('date')))

withend = [r for r in start_today if '〜' in r[2]]
noend = [r for r in start_today if '〜' not in r[2]]
out = io.open('tmp/x0921/today_sale_shape_%s.txt' % tag, 'w', encoding='utf-8')
out.write('today=%s （%s）\n' % (TODAY, tag))
out.write('本日発売の枠 %d枠\n' % len(start_today))
out.write('  締切つき（「〜M/D」がある）  %d枠\n' % len(withend))
out.write('  締切なし                    %d枠\n\n' % len(noend))
out.write('--- 締切なしの枠（昼ヒールで埋まるはず・先頭30）---\n')
for r in noend[:30]:
    out.write('  id%-6s %-10s %s\n' % (r[0], r[1], r[2][:66]))
out.close()
print('%s: 本日発売 %d枠（締切つき %d / 締切なし %d）'
      % (tag, len(start_today), len(withend), len(noend)))
