# -*- coding: utf-8 -*-
"""7165 博多・天神落語まつり 2026＝ぴあが後から売り出した枠が入っていなかった（2026-09-14 夜・会期の直しを試して見つけた）。
ぴあ b2669778 の全24券種（--json）で、買える6枠と登録4枠を「公演日・会場・締切」で突き合わせた:
  登録済み＝10/30 FFG（F-1）・10/30 西鉄（N-1）・10/31 JR九州（J-2 か J-3 のどちらか1つ）
  足す＝10/30 JR九州（J-1・〜10/29）／10/31 JR九州のもう1回（J-3・〜10/30）／11/1 FFG（F-5・〜10/31）
  印＝10/31 FFG（F-3）は予定枚数終了＝売り切れの印（消さない）
10/31 JR九州は同じ会場・同じ日・同じ締切の2回＝見分けるために回の番号（J-2・J-3）を付ける。
使い方: python tmp/fix_7165_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = [x for x in events if x['id'] == 7165][0]
T = {t['type']: t for t in e['tickets']}

ffg31 = '一般発売【FFGホール】（福岡 10/31公演）〜10/30 23:59'
jr31 = '一般発売【JR九州ホール】（福岡 10/31公演）〜10/30 23:59'
assert ffg31 in T and jr31 in T, '登録の枠が見つからない'
T[ffg31]['soldout'] = True
T[ffg31]['soldoutSince'] = TODAY
T[jr31]['type'] = '一般発売【JR九州ホール J-2】（福岡 10/31公演）〜10/30 23:59'
add = [
    {'type': '一般発売【JR九州ホール】（福岡 10/30公演）〜10/29 23:59', 'date': '2026-10-29'},
    {'type': '一般発売【JR九州ホール J-3】（福岡 10/31公演）〜10/30 23:59', 'date': '2026-10-30'},
    {'type': '一般発売【FFGホール】（福岡 11/1公演）〜10/31 23:59', 'date': '2026-10-31'},
]
have = {t['type'] for t in e['tickets']}
for a in add:
    assert a['type'] not in have, '既にある: %s' % a['type']
e['tickets'] = sorted(e['tickets'] + add, key=lambda t: t['date'])
for t in e['tickets']:
    print('  %s ｜締切 %s%s' % (t['type'], t['date'], '｜売り切れ' if t.get('soldout') else ''))
print('枠 %d（足す3・印1・名前の書き替え1）' % len(e['tickets']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
