# -*- coding: utf-8 -*-
"""push前の独立検証（scratchpad/pushcheck_*_result.json）で「予定枚数終了」と読めた枠のうち、
登録済みの枠に売り切れの印を付ける（2026-09-14 朝）。消さない＝soldout:true ＋ soldoutSince（DELETE_GATE 1.）。
tools/mark_soldout.py はエントリ単位（ぴあに1枠でも買える枠があれば alive）なので、会場ごとの売り切れを拾えない。

当て方（登録の券種名から公演を読んで、エージェントの枠と突き合わせる）:
  ・登録の券種名「一般発売（香川・愛媛 10/21〜10/23公演）…」から 県の集合 と 公演日の範囲 を読む
  ・エージェントの「一般発売」系の枠で、その県・その日付範囲に入るものが**1つ以上あり、全部が予定枚数終了**なら印
  ・登録の券種名が「一般発売」で始まる枠だけを対象にする（先行・プレリザーブは窓が別＝取り違えない）
  ・EXTRA＝一般発売以外で、名前まで照らして確かめた枠（2500 ドラクエの4次プリセール＝単日・通しとも予定枚数終了）
  ・未登録の売り切れ公演は足さない（見せるべき買える枠ではない）
使い方: python tmp/mark_soldout_pushcheck_0914.py <id,id,...> [--apply]
"""
import datetime
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
TODAY = datetime.date.today().isoformat()
IDS = [int(x) for x in sys.argv[1].split(',') if x.strip()]
EXTRA = {2500: ['4次プリセール【単日券】（東京 12/30〜R9年 1/1公演）', '4次プリセール【通し券】（東京 12/30〜R9年 1/1公演）']}

res = {}
for p in glob.glob(os.path.join(SP, 'pushcheck_*_result.json')):
    for r in json.load(io.open(p, encoding='utf-8')):
        res[r['id']] = r

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def pshort(p):
    p = unicodedata.normalize('NFKC', p or '')
    return p if p == '北海道' else re.sub(r'(都|府|県)$', '', p)


def show_span(ty):
    """（香川・愛媛 10/21〜10/23公演）→ ({'香川','愛媛'}, '2026-10-21', '2026-10-23')"""
    mm = re.search(r'（([^（）]*?)\s*((?:R9年\s*)?\d{1,2}/\d{1,2})(?:\s*\d{1,2}:\d{2})?(?:〜((?:R9年\s*)?\d{1,2}/\d{1,2}))?公演）', ty or '')
    if not mm:
        return None
    prefs = {x for x in re.split(r'[・/／]', mm.group(1)) if x}

    def iso(s):
        y = 2027 if 'R9年' in s else 2026
        mo, d = re.search(r'(\d{1,2})/(\d{1,2})', s).groups()
        return '%04d-%02d-%02d' % (y, int(mo), int(d))
    a = iso(mm.group(2))
    b = iso(mm.group(3)) if mm.group(3) else a
    if b < a:
        b = '2027' + b[4:]
    return prefs, a, b


n = 0
for i in IDS:
    e, r = by.get(i), res.get(i)
    if not e or not r:
        print('id%s 登録かエージェントの結果が無い＝飛ばす' % i)
        continue
    gen = [s for s in r.get('slots') or [] if '一般' in unicodedata.normalize('NFKC', s.get('name') or '')]
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if t.get('soldout'):
            continue
        hit = any(ty.startswith(x) for x in EXTRA.get(i, []))
        if not hit and ty.startswith('一般発売'):
            sp = show_span(ty)
            if sp:
                prefs, a, b = sp
                cover = [s for s in gen if pshort(s.get('pref')) in prefs and a <= (s.get('show_date') or '') <= b]
                hit = bool(cover) and all(s.get('state') == '予定枚数終了' for s in cover)
        if hit:
            print('id%-5s 印 %s' % (i, ty))
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            n += 1
print('売り切れの印 %d枠' % n)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了')
