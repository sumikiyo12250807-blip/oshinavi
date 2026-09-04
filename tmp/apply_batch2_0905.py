# -*- coding: utf-8 -*-
"""e+「受付中」ぶんを index.html に反映する（2026-09-05・第2便）。

同名の既存エントリがある10件は、新規エントリを作らず**既存に足りない分だけ**入れる:
  ・候補の枠の (県, M/D公演, 締切日) が既存に無い → **足す**（＝別の販売窓＝買える枠の取りこぼし）
  ・同じ (県, M/D公演, 締切日) が既にある      → **足さない**（売り場が違うだけの同じ販売窓）
    ただし既存の枠に `url` が無ければ、候補の会場別URLを**焼き込む**（[[feedback_tour_per_ticket_url]]）
  ・既存の枠は1本も消さない・書き換えない（url が空の時だけ埋める）

🚨 [[feedback_dedup_badges_keeps_urls]] は「**既存のバッジを畳む(消す)な**」というルール。
   「別の売り場のコピーを足せ」ではない。買い口は [[feedback_vendor_priority]] のとおり1つでよい。

残りは新規エントリとして投入する（id は実行時の最大id+1から）。

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, io, re, datetime, unicodedata

PATH = 'index.html'
TODAY = datetime.date.today().isoformat()
WD = '月火水木金土日'

PREF = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
        '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|'
        '愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')
PREF_SET = set(PREF.split('|'))
RE_SLOT = re.compile(r'[（(]\s*((?:%s)(?:都|府|県)?)[^）)]*?(\d{1,2})/(\d{1,2})' % PREF)

# 候補id → 統合先の既存id（dup3_0905.py の判定）
LINK = {6960: 1477, 6965: 2325, 6976: 4240, 6981: 5784, 6984: 5762, 6987: 5766,
        6958: 5879, 6980: 5251, 6989: 3892, 6994: 579}


def perf(t):
    out = set()
    for m in RE_SLOT.finditer(t.get('type') or ''):
        p = m.group(1)
        if p not in PREF_SET:
            p = re.sub(r'[都府県]$', '', p)
        out.add((p, int(m.group(2)), int(m.group(3))))
    return out


def keys(t):
    return {(p, mo, d, t.get('date')) for (p, mo, d) in perf(t)}


h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
maxid = max(by)

built = {b['id']: b for b in json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))}

log = io.open('tmp/apply_batch2_0905.txt', 'w', encoding='utf-8')
n_add = n_url = 0

for cid, tid in LINK.items():
    b, e = built[cid], by[tid]
    have = set()
    for t in e['tickets']:
        have |= keys(t)
    added, urled = [], []
    for t in b['tickets']:
        k = keys(t)
        if not k:
            continue
        if k & have:
            # 同じ販売窓が既にある → 足さない。url が空の既存枠だけ埋める
            for et in e['tickets']:
                if (keys(et) & k) and not et.get('url') and t.get('url'):
                    et['url'] = t['url']
                    urled.append(et['type'])
                    n_url += 1
            continue
        e['tickets'].append(t)
        have |= k
        added.append(t)
        n_add += 1
    # 会場を候補側とユニオンにする（足した公演の会場が抜けないように）
    if added:
        def venues(x):
            v = re.sub(r'^全国ツアー（|）$', '', x.get('venue') or '')
            return [s.strip() for s in re.split(r'[／]', v) if s.strip()]
        vs = venues(e)
        for v in venues(b):
            if v not in vs:
                vs.append(v)
        e['venue'] = ('全国ツアー（%s）' % '／'.join(vs)) if len(vs) > 1 else (vs[0] if vs else e.get('venue'))
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
    if added or urled:
        e['verified'] = True
        e['verifiedAt'] = TODAY
    log.write('■ 既存id%d %s ／ %s\n' % (tid, e.get('artist'), e.get('name')))
    log.write('   足した枠 %d本 / URLを焼いた既存枠 %d本 / 枠合計 %d本\n' % (len(added), len(urled), len(e['tickets'])))
    for t in added:
        log.write('     + %s ｜ 締切%s ｜ %s\n' % (t['type'], t['date'], t.get('url', '')))
    log.write('\n')

# --- 新規 ---------------------------------------------------------------
new, nid = [], maxid + 1
EXCLUDE = {6979}   # ゲートA FAIL（同じ文言の券種が実ページに2〜3行・ビルドが1本に潰した）
for i in sorted(built):
    if i in LINK or i in EXCLUDE:
        continue
    b = built[i]
    b['id'] = nid
    nid += 1
    new.append(b)
json.dump(new, io.open('tmp/batch2_new_0905.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

log.write('既存へ足した枠 合計 %d本 / URLを焼いた枠 %d本\n' % (n_add, n_url))
log.write('新規エントリ %d件（id%d〜%d・枠%d本）\n'
          % (len(new), new[0]['id'], new[-1]['id'], sum(len(x['tickets']) for x in new)))
log.close()

bak = 'index.html.bak_0905_batch2merge'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])

print('MERGE_ADD=%d URL_BURN=%d NEW=%d id%d..%d backup=%s'
      % (n_add, n_url, len(new), new[0]['id'], new[-1]['id'], bak))
