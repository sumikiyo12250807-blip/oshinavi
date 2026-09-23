# -*- coding: utf-8 -*-
"""ヒールを当てたら必ずやる突合（DELETE_GATE 5章）。

安全弁は「公演単位」でしか比べないので、**同じ公演の券種違いが丸ごと消えても気づかない**
（2026-09-01＝阪神×広島9/17が12枠→1枠）。ここで適用前のバックアップと現物を
エントリごとに「画面に出る枠」の数で比べる。
出力: tmp/x0920/heal_compare.md
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
BEFORE = 'tmp/x0920/before_heal_night.html'


def load(p):
    h = io.open(p, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    return {e['id']: e for e in json.loads(m.group(2))}


def visible(t):
    # today は当日。soldout / saleUntilSoldOut は常に表示（DELETE_GATE 5章の定義そのまま）
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


def key(t):
    # 「9/1 10:00発売」→「〜12/20 23:59」に書き換わっただけの枠を「消えた」と数えない
    s = re.sub(r'\d{1,2}/\d{1,2}(\s*\d{1,2}:\d{2})?', '', t.get('type') or '')
    return re.sub(r'[〜~\s]+', '', s)


a, b = load(BEFORE), load('index.html')
shrunk, grew, lost_entries = [], [], []
for i, ea in a.items():
    eb = b.get(i)
    if eb is None:
        lost_entries.append((i, ea.get('artist')))
        continue
    va = {key(t) for t in (ea.get('tickets') or []) if visible(t)}
    vb = {key(t) for t in (eb.get('tickets') or []) if visible(t)}
    if va - vb:
        shrunk.append((i, ea.get('artist'), len(va), len(vb), sorted(va - vb)[:6]))
    elif len(vb) > len(va):
        grew.append((i, ea.get('artist'), len(va), len(vb)))

with io.open('tmp/x0920/heal_compare.md', 'w', encoding='utf-8') as f:
    f.write('# ヒール適用の突合（%s）\n\n適用前 %d件 / 適用後 %d件\n' % (TODAY, len(a), len(b)))
    f.write('\n## 🚨画面に出る枠が減ったエントリ … %d件\n\n' % len(shrunk))
    for i, n, ca, cb, lost in shrunk:
        f.write('- id=%s %s（%d→%d枠）消えた: %s\n' % (i, (n or '')[:40], ca, cb, lost))
    f.write('\n## 増えたエントリ … %d件\n\n' % len(grew))
    for i, n, ca, cb in grew[:40]:
        f.write('- id=%s %s（%d→%d枠）\n' % (i, (n or '')[:40], ca, cb))
    f.write('\n## 消えたエントリ … %d件\n\n' % len(lost_entries))
    for i, n in lost_entries[:40]:
        f.write('- id=%s %s\n' % (i, (n or '')[:40]))
print('減った %d / 増えた %d / 消えたエントリ %d' % (len(shrunk), len(grew), len(lost_entries)))
