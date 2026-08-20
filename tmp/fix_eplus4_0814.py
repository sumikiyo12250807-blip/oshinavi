# -*- coding: utf-8 -*-
"""e+の実ページ（reconcile_eplusで裏取り済み）に合わせて4エントリのticketsを直す。

  dump  : 現状のticketsを表示するだけ
  apply : index.html に適用（CRLF保持・EVENTS配列をjsonで読み書き）

根拠（2026-08-14 に e+ 個別ページを機械パースして確認した実窓）:
  1037 t0  open 2026-05-22 10:00〜2026-08-15 20:00   （登録は8/12 18:00＝古い）
  1619 t1-t4 締切一致・同日昼夜の公演時刻がバッジに無い（LD 13:30/16:30）
  1619 t5,t6 群馬9/26＝全窓ended「受付は全て終了しました」→ 死枠
  3032 t0  before 2026-08-14 12:00〜2026-08-30 23:59 → 発売前化
  3032 t1  open 2026-08-08 12:00〜2026-08-19 23:59
  3032 t2,t3,t4 全窓ended → 死枠
  3088 t0,t1 ページ404＋公演日が過去(8/10,8/11) → 死枠
  3088 t2  open 〜2026-08-15 23:59 ／ t3 open 〜2026-08-16 23:59
"""
import re, json, io, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv

PATH = 'index.html'
h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
byid = {e['id']: e for e in EV}

# --- 直す内容 -------------------------------------------------------------
# (id, ticket index) -> {'type':..., 'date':..., 'startDate':...} / 'DROP'
EDITS = {
    (1037, 0): {'type': '一般発売（兵庫 8/16公演）〜8/15 20:00', 'date': '2026-08-15'},
    (1619, 1): {'type': '一般発売＜昼公演＞（和歌山 9/5 13:30公演）〜9/4 18:00'},
    (1619, 2): {'type': '一般発売＜夜公演＞（和歌山 9/5 16:30公演）〜9/4 18:00'},
    (1619, 3): {'type': '一般発売＜昼公演＞（滋賀 9/6 13:30公演）〜9/5 18:00'},
    (1619, 4): {'type': '一般発売＜夜公演＞（滋賀 9/6 16:30公演）〜9/5 18:00'},
    (1619, 5): 'DROP',
    (1619, 6): 'DROP',
    (3032, 0): {'type': '抽選○プレオーダー受付（大阪府 10/2公演）8/14 12:00発売',
                'startDate': '2026-08-14', 'date': '2026-08-30'},
    (3032, 1): {'type': '抽選プレオーダー受付（福岡県 10/4公演）〜8/19 23:59', 'date': '2026-08-19'},
    (3032, 2): 'DROP',
    (3032, 3): 'DROP',
    (3032, 4): 'DROP',
    (3088, 0): 'DROP',
    (3088, 1): 'DROP',
    (3088, 2): {'type': '先着一般発売（東京都 8/16公演）〜8/15 23:59', 'date': '2026-08-15'},
    (3088, 3): {'type': '先着一般発売（東京都 8/17公演）〜8/16 23:59', 'date': '2026-08-16'},
}

# 枠を落としたあとの千秋楽（＝残る公演の最終日）。並び順の基準なので明示で置く。
NEW_DATE = {1619: '2026-09-06', 3032: '2026-10-04'}

for i in (1037, 1619, 3032, 3088):
    e = byid[i]
    print('\n=== id=%d %s  date=%s' % (i, e.get('artist', ''), e.get('date')))
    keep = []
    for ti, t in enumerate(e.get('tickets') or []):
        ed = EDITS.get((i, ti))
        if ed == 'DROP':
            print('  t%d ❌落とす: %s' % (ti, t.get('type')))
            continue
        if ed:
            print('  t%d 🔧%s' % (ti, t.get('type')))
            print('      → %s' % ed.get('type', t.get('type')))
            if 'date' in ed and ed['date'] != t.get('date'):
                print('      締切 %s → %s' % (t.get('date'), ed['date']))
            if 'startDate' in ed:
                print('      発売日 %s → %s' % (t.get('startDate'), ed['startDate']))
            t = dict(t)
            t.update(ed)
        keep.append(t)
    e['tickets'] = keep
    if i in NEW_DATE and e.get('date') != NEW_DATE[i]:
        print('  📅千秋楽 %s → %s' % (e.get('date'), NEW_DATE[i]))
        e['date'] = NEW_DATE[i]

if not APPLY:
    print('\n（提案のみ。適用は --apply）')
    sys.exit(0)

bak = PATH + '.bak_0814_eplus_fix'
open(bak, 'w', encoding='utf-8', newline='').write(h)
body = json.dumps(EV, ensure_ascii=False, indent=2)
if '\r\n' in h:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
out = h[:m.start(2)] + body + h[m.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('\n=== 適用した (backup: %s) ===' % bak)
