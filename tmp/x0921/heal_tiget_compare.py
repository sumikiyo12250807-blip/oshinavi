# -*- coding: utf-8 -*-
"""TIGETヒールの前後で「画面に出る枠の数」が**本当に減った**エントリだけを数える。
tmp/heal_head_compare_1805.py は「キーが変わった枠」を全部 gone と出すので、
「発売〜 → 〜締切」に書き換わっただけ・当日券が増えて名前が変わっただけでも鳴る。
ここでは ①数が減った ②売り切れ印の枠が消えた の2つだけを事故として拾う
（[[feedback_heal_flattens_ticket_types]]／[[feedback_soldout_keep_visible]]）。
"""
import datetime, io, json, re, subprocess, sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
TODAY = datetime.date.today().isoformat()


def events(text):
    return {e['id']: e for e in json.loads(
        re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


head = events(subprocess.run(['git', 'show', 'HEAD:index.html'],
                             capture_output=True).stdout.decode('utf-8'))
now = events(io.open('index.html', encoding='utf-8', newline='').read())

out = io.open('tmp/x0921/heal_tiget_compare.txt', 'w', encoding='utf-8')
dec, sold_gone, same, inc = [], [], 0, 0
for i, e in sorted(head.items()):
    n = now.get(i)
    if n is None:
        dec.append((i, e, None, None))
        continue
    v_old = [t for t in (e.get('tickets') or []) if H.visible_slot(t, TODAY)]
    v_new = [t for t in (n.get('tickets') or []) if H.visible_slot(t, TODAY)]
    if len(v_new) < len(v_old):
        dec.append((i, e, len(v_old), len(v_new)))
    elif len(v_new) > len(v_old):
        inc += 1
    else:
        same += 1
    # 売り切れ印の枠が消えていないか（数が同じでも起きる）
    so_old = {H.slot_key(t) for t in v_old if t.get('soldout')}
    so_new = {H.slot_key(t) for t in v_new if t.get('soldout')}
    if so_old - so_new:
        sold_gone.append((i, e, sorted(so_old - so_new)))

out.write('=== TIGETヒールの前後（today=%s）===\n' % TODAY)
out.write('枠が減ったエントリ %d件 / 増えた %d件 / 同数 %d件\n' % (len(dec), inc, same))
out.write('売り切れ印の枠が消えたエントリ %d件\n\n' % len(sold_gone))
out.write('--- 減ったもの ---\n')
for i, e, a, b in dec:
    out.write('id%-6s %-34s %s枠 → %s枠\n'
              % (i, (e.get('name') or e.get('artist') or '')[:34], a, b))
out.write('\n--- 売り切れ印が消えたもの ---\n')
for i, e, ks in sold_gone:
    out.write('id%-6s %-34s\n' % (i, (e.get('name') or '')[:34]))
    for k in ks:
        out.write('    %s\n' % (k,))
out.close()
print('減った%d件 / 増えた%d件 / 同数%d件 / 売り切れ印が消えた%d件 → tmp/x0921/heal_tiget_compare.txt'
      % (len(dec), inc, same, len(sold_gone)))
