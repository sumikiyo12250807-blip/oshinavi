# -*- coding: utf-8 -*-
"""新着50件を組み立てる（投入前の最終形）。

内訳＝ぴあ44件（締切が今日/明日の2件を除外）＋ 楽天6件（ウルトラヒーローズ4会場を1エントリに統合）。

守っているルール:
- 締切が今日/明日の枠しか無いものは載せない（[[feedback_presale_first_harvest]]のコロラリー）
- ツアー・複数会場は1エントリ（[[feedback_tour_consolidate]]）＋各バッジに会場別URL（[[feedback_tour_per_ticket_url]]）
- id は投入前に通し番号で振り直す（投入後の振り直しは禁止＝[[feedback_new_list_order_lock]]）
- _genre は下書きのみ（振り分けはユーザー合図後＝[[feedback_new_pool_ok_before_assign]]）
"""
import datetime
import json
import re
import unicodedata

TODAY = datetime.date.today().isoformat()
TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

pia = json.load(open('tmp/built_pia_0730b.json', encoding='utf-8'))
rak = json.load(open('tmp/built_rakuten_0730.json', encoding='utf-8'))

log = []

# ---- ① ぴあ：最遅締切が今日/明日のものは落とす ----
def last_date(e):
    ts = e.get('tickets') or []
    return max((t.get('date') or '') for t in ts) if ts else ''


pia_keep, pia_drop = [], []
for e in pia:
    ld = last_date(e)
    if ld <= TOMORROW:
        pia_drop.append((e, ld))
    else:
        pia_keep.append(e)
log.append(f'ぴあ {len(pia)}件 → 残 {len(pia_keep)}件 / 締切が今日・明日で除外 {len(pia_drop)}件')
for e, ld in pia_drop:
    log.append(f'   除外 {e.get("artist")[:44]}（最遅締切 {ld}）')

# ---- ② 楽天：ウルトラヒーローズを1エントリに統合 ----
def base_name(s):
    # 「… in 千葉県柏」「… in 仙台」の会場サフィックスを落として同一興行を束ねる
    return re.sub(r'\s*in\s*[^\s]*$', '', unicodedata.normalize('NFKC', s or '')).strip()


groups = {}
for e in rak:
    groups.setdefault(base_name(e.get('artist')), []).append(e)

rak_out = []
for key, es in groups.items():
    if len(es) == 1:
        rak_out.append(es[0])
        continue
    es.sort(key=lambda x: x['date'])
    head = dict(es[0])
    head['artist'] = head['name'] = key
    venues, prefs, tickets = [], [], []
    for e in es:
        if e.get('venue') and e['venue'] not in venues:
            venues.append(e['venue'])
        if e.get('prefecture') and e['prefecture'] not in prefs:
            prefs.append(e['prefecture'])
        tickets += (e.get('tickets') or [])
    head['venue'] = '全国ツアー（%s）' % '／'.join(venues)
    head['prefecture'] = '全国'
    head['date'] = max(e['date'] for e in es)
    first = min(e['date'] for e in es)

    def jp(iso):
        y, m, d = (int(x) for x in iso.split('-'))
        wd = '月火水木金土日'[datetime.date(y, m, d).weekday()]
        return f'{y}年{m}月{d}日({wd})'

    head['dateLabel'] = f'{jp(first)}〜{jp(head["date"])} 全国ツアー'
    # 枠は公演日順→締切順で並べる（バッジの見え方を安定させる）
    tickets.sort(key=lambda t: (t.get('startDate') or '', t.get('date') or ''))
    head['tickets'] = tickets
    rak_out.append(head)
    log.append(f'統合 {key[:44]} ← {len(es)}会場 / 枠{len(tickets)}  県={"・".join(prefs)}')

# ---- ③ _genre 下書きの穴埋め（空のものだけ・名前で判断できるものに限る） ----
DRAFT = {
    '花火': 'hanabi',
    'ウルトラヒーローズ': 'kids',
}
for e in rak_out:
    if e.get('_genre'):
        continue
    nm = e.get('artist') or ''
    for kw, g in DRAFT.items():
        if kw in nm:
            e['_genre'] = g
            if g == 'kids':
                e['_extraGenres'] = ['anime']
            log.append(f'_genre下書き {nm[:40]} → {g}{"+anime" if g == "kids" else ""}（「{kw}」で判定）')
            break
    else:
        log.append(f'⚠️_genre が空のまま {nm[:50]}（ユーザーに相談）')

# ---- ③.5 既存と同一ページの重複を落とす（tmp/predup_0730.py で機械検出した分） ----
# rtg2672＝既存3239 大阪芸術花火2026 が市民割枠まで既に持っている
# rtctnp6＝既存1768 Na Pookela ナーポオケラ 2026 と同一ページ（別名表記）
DUP_CODES = {'rtg2672', 'rtctnp6'}
kept = []
for e in rak_out:
    s = json.dumps(e, ensure_ascii=False)
    hit = [c for c in DUP_CODES if c in s]
    if hit:
        log.append(f'重複で除外 {(e.get("artist") or "")[:44]}（{hit[0]}＝既存と同一ページ）')
    else:
        kept.append(e)
rak_out = kept

# ---- ④ 50件に切って通し番号を振り直す ----
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)

merged = pia_keep + rak_out
if len(merged) > 50:
    log.append(f'⚠️ {len(merged)}件あるので先頭50件に切る（1バッチ50件上限）')
    merged = merged[:50]

for n, e in enumerate(merged):
    e['id'] = maxid + 1 + n

json.dump(merged, open('tmp/new50_0730.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

nt = sum(len(e.get('tickets') or []) for e in merged)
log.append('')
log.append(f'=== 投入候補 {len(merged)}件 / 枠 {nt} / id {merged[0]["id"]}..{merged[-1]["id"]} → tmp/new50_0730.json ===')
src = {}
for e in merged:
    s = 'rakuten' if (e.get('links') or {}).get('rakuten') else 'pia'
    src[s] = src.get(s, 0) + 1
log.append(f'   ソース別: {src}')
open('tmp/assemble_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('wrote tmp/assemble_0730.txt / tmp/new50_0730.json  entries=%d' % len(merged))
