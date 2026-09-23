# -*- coding: utf-8 -*-
"""ぴあで「予定枚数終了」ではなく終わっていた3件に、いちばん新しい満了枠へ印を付ける（mark_soldout と同じ考え方）。
  id4114 Yung Kai＝抽選受付終了（抽選結果発表前）→ 先行終了（soldout+presaleEnded）
  id5669 フォーレ四重奏団 第1夜＝「販売を終了致しました」→ 販売終了（soldout+saleEnded）
  id1149 いぎなり東北産＝「販売終了」→ 販売終了
根拠＝tmp/mark_soldout_0922.txt（ぴあ実ページの判定・9/22朝）。
"""
import io, json, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
KIND = {4114: 'presaleEnded', 5669: 'saleEnded', 1149: 'saleEnded'}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    k = KIND.get(e['id'])
    if not k:
        continue
    ts = e.get('tickets') or []
    last = max(t.get('date') or '' for t in ts)
    for t in ts:
        if (t.get('date') or '') == last and not t.get('soldout'):
            t['soldout'] = True
            t[k] = True
            t[k + 'Since'] = TODAY
            print('id%d %s → %s' % (e['id'], t['type'], k))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
