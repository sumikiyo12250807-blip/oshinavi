# -*- coding: utf-8 -*-
"""push 前の抜き取り30件＝別エージェントがぴあからゼロで読んだ結果（scratchpad/pushcheck_0916_result.json）と登録を突き合わせる（読むだけ）。
見るもの:
 ① 買える枠＝エージェントの受付中・発売前を「券種名＋締切」の組で数えた数 と 登録の画面に出る買える枠（売り切れの印を除く）の数
 ② 登録の締切（〜M/D HH:MM）がエージェントの受付中の締切に1つずつあるか
 ③ 登録で売り切れの印の枠＝その公演日にエージェントの「予定枚数終了」「販売終了」があるか（買える言い方だけなら印が嘘）
使い方: python tmp/compare_pushcheck_0916.py
"""
import datetime
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
TODAY = datetime.date.today().isoformat()
rows = {r['id']: r for r in json.load(io.open(SP + r'\pushcheck_0916_result.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
LIVE = ('受付中', '発売前')


def n(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'\s*／.*$', '', s)
    return re.sub(r'[\s.．。]+', '', s)


def buyable(t):
    if t.get('soldout'):
        return False
    if t.get('saleUntilSoldOut'):
        return True
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def mdhm(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})(?:\s+(\d{1,2}):(\d{2}))?', s or '')
    if not m:
        return ''
    return ('%d/%d %d:%s' % (int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5))) if m.group(4) else '%d/%d' % (int(m.group(2)), int(m.group(3)))


def show_days(ty):
    m = re.search(r'（[^（）]*?((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)(?:\s+\d{1,2}:\d{2})?公演）', ty or '')
    return [re.sub(r'^R\d+年\s*', '', x.strip()) for x in m.group(1).split('〜')] if m else []


bad = 0
for i in sorted(rows):
    r, e = rows[i], by.get(i)
    if not e:
        print('id%d：登録が無い' % i)
        continue
    if r.get('note') and not r.get('slots'):
        print('❓ id%d %s：読めなかった（%s）' % (i, e['name'][:24], r['note'][:60]))
        continue
    slots = r.get('slots') or []
    live = [s for s in slots if s.get('state') in LIVE]
    wins = {(n(s.get('name')), s.get('sale_end') or '', s.get('state')) for s in live}
    ends = {mdhm(s.get('sale_end')) for s in live if s.get('sale_end')}
    # ぴあの枠だけを比べる（飛び先がぴあ、または飛び先が空＝links.pia に飛ぶ枠）。ローチケ・e+・楽天の枠は各社の道具で見る
    pia_t = [t for t in e.get('tickets') or [] if not t.get('url') or 'pia.jp' in (t.get('url') or '')]
    vis = [t for t in pia_t if buyable(t)]
    flags = []
    reg_ends = set()
    for t in vis:
        m = re.search(r'〜((?:R\d+年\s*)?\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2})\s*$', t.get('type') or '')
        if m:
            reg_ends.add(re.sub(r'^R\d+年\s*', '', m.group(1)))
            if not (t.get('startDate') and t['startDate'] > TODAY) and re.sub(r'^R\d+年\s*', '', m.group(1)) not in ends:
                flags.append('登録の締切がぴあの受付中に無い: %s' % t['type'][:50])
    for s in live:
        if s.get('state') == '受付中' and s.get('sale_end') and mdhm(s['sale_end']) not in reg_ends:
            flags.append('ぴあの受付中（〜%s）が登録に無い: %s' % (mdhm(s['sale_end']), (s.get('name') or '')[:30]))
    flags = list(dict.fromkeys(flags))
    for t in pia_t:
        if not t.get('soldout') or (t.get('date') or '') < TODAY and not show_days(t.get('type')):
            continue
        days = set(show_days(t.get('type')))
        mine = [s for s in slots if any(d in mdhm(s.get('show_date', '')[:10]) or mdhm((s.get('show_date') or '')[:10]) == d for d in days)]
        if mine and not any(s.get('state') in ('予定枚数終了', '販売終了', '受付終了') for s in mine):
            flags.append('売り切れの印なのに、その公演日はぴあで買える言い方だけ: %s' % t['type'][:50])
    mark = '✅' if not flags else '⚠️'
    if flags:
        bad += 1
    print('%s id%d %s ｜ %s' % (mark, i, e['name'][:26], ' ／ '.join(flags) if flags else '一致'))
print('\n抜き取り %d件 ／ 疑い %d件' % (len(rows), bad))
