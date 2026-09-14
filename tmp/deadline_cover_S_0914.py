# -*- coding: utf-8 -*-
"""検証S（scratchpad/pushcheck_S_result.json）の「買える枠」が、登録のどれかの枠で覆われているかを
**締切の日付・県・公演日**で確かめる（読むだけ・2026-09-14 昼の前）。
compare_pushcheck は枠の「数」しか比べない＝検証役は公演1日ごとに1行、うちは同じ締切の日をまとめて1枠
なので数が合わないのは当たり前。本当に抜けているのは「その締切・その公演日を覆う登録の枠が無い」ものだけ。
覆う＝登録の枠の date が検証役の締切日と同じ（締切が無い発売前は startDate が発売日と同じ）で、
券種名の（県 M/D〜M/D公演）にその県・その公演日が入っている。
使い方: python tmp/deadline_cover_S_0914.py [S]
出力: tmp/deadline_cover_S_0914.md
"""
import datetime
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
GRP = sys.argv[1] if len(sys.argv) > 1 else 'S'
TODAY = datetime.date.today().isoformat()

src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
rows = json.load(io.open(os.path.join(SP, 'pushcheck_%s_result.json' % GRP), encoding='utf-8'))


def pshort(p):
    p = unicodedata.normalize('NFKC', p or '')
    return p if p == '北海道' else re.sub(r'(都|府|県)$', '', p)


def pshort_set(p):
    """検証係は1枚のカードで複数県を売る枠を「山口県／東京都」とひとまとめで書く＝県の集合にして比べる。"""
    return {pshort(x) for x in re.split(r'[／/・]', unicodedata.normalize('NFKC', p or '')) if x.strip()}


def show_span(ty):
    """（香川・愛媛 10/21〜10/23公演）→ ({'香川','愛媛'}, '2026-10-21', '2026-10-23')。全国は県を問わない。"""
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


def visible(t):
    if t.get('soldout'):
        return False
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


out = io.open('tmp/deadline_cover_%s_0914.md' % GRP, 'w', encoding='utf-8')
W = out.write
W('# 検証%s の買える枠が登録で覆われているか（締切日・県・公演日）%s\n\n' % (GRP, TODAY))
miss_ids = 0
miss_slots = 0
checked = 0
stale = []   # 逆向き＝登録で見えているのに、検証係の読んだ買える枠のどれとも合わない枠
for r in sorted(rows, key=lambda x: x['id']):
    e = by.get(r['id'])
    if not e:
        continue
    tix = [t for t in e.get('tickets') or [] if visible(t)]
    spans = [(t, show_span(t.get('type'))) for t in tix]
    lost = []
    for s in r.get('slots') or []:
        if s.get('state') not in ('受付中', '発売前'):
            continue
        end = (s.get('end') or '')[:10]
        start = (s.get('start') or '')[:10]
        if end and end < TODAY:
            continue
        checked += 1
        sd = s.get('show_date') or ''
        sd_end = s.get('show_date_end') or sd
        pf = pshort_set(s.get('pref'))
        ok = False
        for t, sp in spans:
            day_ok = (end and t.get('date') == end) or (not end and start and t.get('startDate') == start)
            if not day_ok:
                continue
            if not sp:
                ok = True
                break
            prefs, a, b = sp
            if ('全国' in prefs or (pf & prefs) or not pf) and (a <= sd <= b or a <= sd_end <= b or (sd <= a and b <= sd_end)):
                ok = True
                break
        if not ok:
            lost.append(s)
    # 逆向き＝登録で見えている「ぴあの枠」が、検証係の読んだ買える枠のどれかと合うか（締切日・県・公演日）。
    #   合わない＝ぴあではもう買えない（販売終了・予定枚数終了）のに画面では買えるように出ている疑い。
    #   🚨1対1で組む＝同じ締切の枠が4つあって1つだけ予定枚数終了の時、「どれかと合えばよい」だと
    #   残り3つと合ったことにされて隠れる（検証Wの対象はみなこの形）。合う相手の少ない枠から順に、
    #   まだ使っていない買える枠を1つずつ割り当て、相手が残っていない登録の枠を出す。
    live = [s for s in r.get('slots') or [] if s.get('state') in ('受付中', '発売前')]
    pairs = []
    for t, sp in spans:
        u = t.get('url') or (e.get('links') or {}).get('pia') or ''
        if 'pia.jp' not in u:
            continue
        cand = []
        for k, s in enumerate(live):
            end = (s.get('end') or '')[:10]
            start = (s.get('start') or '')[:10]
            if not ((end and t.get('date') == end) or (t.get('startDate') and start and t.get('startDate') == start)
                    or (not end and t.get('date') == start)):
                continue
            if not sp:
                cand.append(k)
                continue
            prefs, a, b = sp
            sd = s.get('show_date') or ''
            sd_end = s.get('show_date_end') or sd
            pf = pshort_set(s.get('pref'))
            if ('全国' in prefs or (pf & prefs) or not pf) and (a <= sd <= b or a <= sd_end <= b or (sd <= a and b <= sd_end)):
                cand.append(k)
        pairs.append((t, cand))
    used = set()
    for t, cand in sorted(pairs, key=lambda x: len(x[1])):
        free = [k for k in cand if k not in used]
        if free:
            used.add(free[0])
        else:
            stale.append((r['id'], (e.get('name') or '')[:30], t.get('type'), t.get('date')))
    if lost:
        miss_ids += 1
        miss_slots += len(lost)
        W('- **id%s %s**（登録の見える枠 %d）\n' % (r['id'], (e.get('name') or '')[:40], len(tix)))
        for s in lost[:12]:
            W('  - 覆う登録なし：%s ｜%s %s〜%s ｜%s ｜%s〜%s\n' % (
                s.get('name'), s.get('pref'), s.get('show_date'), s.get('show_date_end') or '',
                s.get('state'), s.get('start') or '', s.get('end') or ''))
        if len(lost) > 12:
            W('  - ほか %d枠\n' % (len(lost) - 12))
        W('  - 登録：%s\n' % ' ／ '.join(t.get('type') for t in tix[:6]))
W('\n## 逆向き＝登録で見えているのに、ぴあで買える枠のどれとも合わない %d枠\n\n' % len(stale))
for i, n, ty, d in stale:
    W('- id%s %s ｜%s（date %s）\n' % (i, n, ty, d))
W('\n読めた %d件 / 突き合わせた買える枠 %d / 覆う登録が無い枠がある %d件・%d枠 / 逆向きで合わない登録の枠 %d\n' % (
    len(rows), checked, miss_ids, miss_slots, len(stale)))
out.close()
print('読めた %d件 / 突き合わせた買える枠 %d / 覆う登録が無い枠がある %d件・%d枠 / 逆向きで合わない登録の枠 %d → tmp/deadline_cover_%s_0914.md' % (
    len(rows), checked, miss_ids, miss_slots, len(stale), GRP))
