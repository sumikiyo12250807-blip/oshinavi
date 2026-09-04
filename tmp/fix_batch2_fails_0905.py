# -*- coding: utf-8 -*-
"""reconcile_eplus が FAIL を出した枠を落とす（2026-09-05・第2便の後始末）。

なぜ出たか＝**e+のツアーは、個別の -P ページに販売窓を出さないことがある**。
ビルドは base ページの窓を各公演にコピーして付けるので、
reconcile が「その-Pページには開いている窓が無い」＝`c-死枠` として弾く。
そのまま載せると、**バッジを押しても買えないページに着く**。だから落とす。

🚨**バックアップで丸ごと戻さない**＝別セッションがこのあと既存エントリに枠を足しているので、
   戻すとその分が消える。**FAILの枠だけを index 指定で抜く**（追記は末尾に付くので既存indexは動かない）。

やること:
  1) 今日入れた新規(6948〜6985) … FAILの枠だけ抜く。0本になったらエントリごと落として NEW_ORDER からも外す
  2) 既存へ足した10件 … **今日足した分（＝投入前の本数より後ろ）のFAILだけ**抜く。
     投入前からある枠は1本も触らない（FAILが出ていても報告だけ）
  3) 今日足した分が全部消えたエントリは、venue/date/dateLabel を投入前の姿に戻す

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, io, re, datetime

PATH = 'index.html'
BAK = 'index.html.bak_0905_batch2merge'   # 第2便を当てる前
TODAY = datetime.date.today().isoformat()
WD = '月火水木金土日'
NEW_LO, NEW_HI = 6948, 6985
MERGED = [5879, 5251, 5784, 5766, 3892, 1477, 2325, 4240, 5762, 579]

fails = {}
for ln in io.open('tmp/reconcile_eplus_batch2_0905.txt', encoding='utf-8'):
    m = re.match(r'\s*id(\d+) t(\d+) \[', ln)
    if m:
        fails.setdefault(int(m.group(1)), set()).add(int(m.group(2)))

h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

hb = io.open(BAK, encoding='utf-8', newline='').read()
prev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', hb, re.S).group(1))}

log = io.open('tmp/fix_batch2_fails_0905.txt', 'w', encoding='utf-8')
dropped_entries, n_drop, n_keep, n_left = [], 0, 0, 0

# --- 1) 新規エントリ -----------------------------------------------------
for i in range(NEW_LO, NEW_HI + 1):
    e = by.get(i)
    if not e or i not in fails:
        continue
    n0 = len(e['tickets'])
    for ti in sorted(fails[i], reverse=True):
        if 0 <= ti < len(e['tickets']):
            del e['tickets'][ti]
            n_drop += 1
    log.write('新規 id%d %s ／ %s ＝ 枠 %d→%d\n' % (i, e['artist'], e['name'], n0, len(e['tickets'])))
    if not e['tickets']:
        dropped_entries.append(i)

# --- 2) 既存へ足した分 ---------------------------------------------------
for tid in MERGED:
    e, p = by.get(tid), prev.get(tid)
    if not e or not p:
        continue
    base = len(p['tickets'])                     # 投入前の本数
    mine_before = len(e['tickets']) - base       # 今日足した本数（このあと別セッションの追記があれば混ざる）
    bad = sorted(fails.get(tid, ()), reverse=True)
    old_bad = [t for t in bad if t < base]
    my_bad = [t for t in bad if t >= base]
    for ti in my_bad:
        if 0 <= ti < len(e['tickets']):
            del e['tickets'][ti]
            n_drop += 1
    left = len(e['tickets']) - base
    n_keep += max(0, left)
    if left <= 0:                                # 今日足した分が全部消えた → 元の姿に戻す
        e['venue'] = p.get('venue')
        e['date'] = p.get('date')
        e['dateLabel'] = p.get('dateLabel')
        e['prefecture'] = p.get('prefecture')
    else:
        days = set()
        for t in e['tickets']:
            for mm in re.finditer(r'(?:(R\d)年\s*)?(\d{1,2})/(\d{1,2})公演', t.get('type') or ''):
                y = 2027 if mm.group(1) else 2026
                try:
                    days.add(datetime.date(y, int(mm.group(2)), int(mm.group(3))))
                except ValueError:
                    pass
        if days:
            lo, hi = min(days), max(days)
            e['date'] = hi.isoformat()

            def jp(d):
                return '%d年%d月%d日(%s)' % (d.year, d.month, d.day, WD[d.weekday()])
            e['dateLabel'] = (jp(lo) + '〜' + jp(hi) + ' 全国ツアー') if lo != hi \
                else (jp(lo) + ' ' + (e.get('prefecture') or ''))
    if old_bad:
        n_left += len(old_bad)
        log.write('⚠️ 既存 id%d ＝ **投入前からある枠**に FAIL %d本（触っていない・要確認）: %s\n'
                  % (tid, len(old_bad), old_bad))
    log.write('既存 id%d %s ＝ 今日足した %d本 → %d本（FAIL %d本を落とした）\n'
              % (tid, e.get('artist'), mine_before, max(0, left), len(my_bad)))

if dropped_entries:
    events = [e for e in events if e['id'] not in dropped_entries]
    log.write('\n枠が0になって落としたエントリ: %s\n' % dropped_entries)
log.write('\n落とした枠 %d本 / 残した追加枠 %d本 / 落としたエントリ %d件 / 元からあるFAIL %d本\n'
          % (n_drop, n_keep, len(dropped_entries), n_left))
log.close()

mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
order = [int(x) for x in re.findall(r'\d+', mo.group(2))]
order = [i for i in order if i not in dropped_entries]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            r'\g<1>[' + ', '.join(str(i) for i in order) + ']', h, count=1)

m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
bak2 = 'index.html.bak_0905_fixfails'
io.open(bak2, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h2[:m2.start()] + m2.group(1) + arr + m2.group(3) + h2[m2.end():])

print('DROP_SLOTS=%d KEEP_ADDED=%d DROP_ENTRIES=%s OLD_FAILS=%d NEW_ORDER=%d backup=%s'
      % (n_drop, n_keep, dropped_entries, n_left, len(order), bak2))
