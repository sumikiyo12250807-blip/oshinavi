# -*- coding: utf-8 -*-
"""バッジ0の救済②＝再ビルドで拾えた枠を既存エントリへ**足すだけ**当てる。

🚨置換は絶対にしない（memory: feedback_build_pia_multiurl_loses_ticket_url の
   「統合・救済・当て直しは追加と補完だけ。置換は枠を殺す」）。
やること＝①既存に無い枠を足す ②url が空の既存枠に url を補完 ③千秋楽が伸びたら date を更新。
"""
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

built = {e['id']: e for e in json.load(open('tmp/_zb_built_0901.json', encoding='utf-8'))}
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EVENTS = json.loads(m.group(2))

added = urlfilled = datemoved = 0
report = []
for e in EVENTS:
    b = built.get(e.get('id'))
    if not b:
        continue
    have = {(t.get('type'), t.get('date')) for t in e.get('tickets', [])}
    lines = []
    for t in b.get('tickets', []):
        k = (t.get('type'), t.get('date'))
        if k in have:
            for ex in e['tickets']:                       # url の補完だけ行う
                if (ex.get('type'), ex.get('date')) == k and not ex.get('url') and t.get('url'):
                    ex['url'] = t['url']; urlfilled += 1
                    lines.append(f"   ○url補完 {t['type']}")
            continue
        e.setdefault('tickets', []).append(dict(t))
        have.add(k); added += 1
        lines.append(f"   + {t['type']} | 締切 {t.get('date')} | {t.get('url') or '(entry links)'}")
    if b.get('date') and b['date'] > (e.get('date') or ''):
        lines.append(f"   公演日 {e.get('date')} → {b['date']}（千秋楽が後ろに伸びた）")
        e['date'] = b['date']; datemoved += 1
    if lines:
        report.append(f"## id={e['id']} {e.get('artist')}\n" + "\n".join(lines))

print("\n\n".join(report))
print(f"\n合計 {len(report)} エントリ / +{added} 枠 / url補完 {urlfilled} / 公演日が伸びた {datemoved}件")

if APPLY:
    NL = '\r\n' if '\r\n' in src else '\n'
    bak = f'index.html.bak_{datetime.date.today():%m%d}_zbrescue'
    open(bak, 'w', encoding='utf-8', newline='').write(src)
    body = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
    open(f'logs/rescued_{datetime.date.today():%Y-%m-%d}.md', 'w', encoding='utf-8').write(
        f"# {datetime.date.today():%Y-%m-%d} 朝の便 バッジ0の救済（追加のみ・置換なし）\n\n"
        "検出＝`check_zero_badge.js` の要対応104件 → `reconcile_pia.py --ids` で MISSING が出た39件。\n"
        "ぴあURLを全部渡して `build_pia_entries.py` で再導出し、**既存に無い枠だけを足した**。\n\n"
        + "\n\n".join(report)
        + f"\n\n合計 {len(report)} エントリ / +{added} 枠 / url補完 {urlfilled} / 公演日が伸びた {datemoved}件\n")
    print(f"✅ 適用（backup {bak}）")
else:
    print("（ドライラン。当てるなら --apply）")
