# -*- coding: utf-8 -*-
"""表示バッジが完全一致する重複ticketを意図集約（1枚に）。

朝ルーチン常設。heal_stale_deadlines / build_pia_entries でぴあを再パースすると
フェスの個別公演などが「表示上まったく同じバッジ」として何枚も復活するため、
ヒールの後に必ず流して畳む。

判定は dispkey（画面に出るフィールド）が完全一致するものだけ。url違い＝見た目同じ
なので畳む。席種違い・全国ツアーの会場別枠は type/dateLabel が違うので残る。

  python tools/dedup_badges.py           走査のみ
  python tools/dedup_badges.py --apply   適用（backupを取る）
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))


def dispkey(t):
    # 画面表示に効くフィールド。urlは表示に出ないので除外＝同じ見た目なら重複。
    return (t.get('type', ''), t.get('startDate'), t.get('date'),
            t.get('badge', ''), t.get('dateLabel', ''), t.get('saleUntilSoldOut'))


def dedup(ts):
    seen, out = set(), []
    for t in ts:
        k = dispkey(t)
        if k in seen:
            continue
        seen.add(k); out.append(t)
    return out


report = []
for e in E:
    ts = e.get('tickets', [])
    nd = dedup(ts)
    if len(nd) < len(ts):
        report.append((e['id'], e.get('artist', '')[:34], len(ts), len(nd)))

report.sort(key=lambda x: x[2] - x[3], reverse=True)
print(f'=== 重複バッジ持ちエントリ {len(report)}件（表示枠→集約後）===')
for i, a, before, after in report:
    print(f'  id={i:<5} {before:>2}→{after:<2}  {a}')

if '--apply' in sys.argv:
    changed = tot_removed = 0
    for e in E:
        ts = e.get('tickets', [])
        nd = dedup(ts)
        if len(nd) < len(ts):
            tot_removed += len(ts) - len(nd)
            e['tickets'] = nd; changed += 1
    bak = f'index.html.bak_{datetime.date.today():%m%d}_dedup_badges'
    open(bak, 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(E, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print(f'\n=== {changed}エントリ集約 / 重複枠 {tot_removed}件除去 (backup {bak}) ===')
