# -*- coding: utf-8 -*-
"""ぴあ受付中（演劇・クラシック・イベント・9/22夜）で「売切」等で組めなかった件を、印付きの枠として組み立てる。
ルール（2026-09-18 ユーザー決定）＝公演がこれからなら売切れ・販売終了でも印を付けて載せる。

build_pia_entries.build() をそのまま使い、次の2点だけ差し替える（このプロセスの中だけ）:
  ・parse_cards: 公演日がこれから（perf_end>=今日）で、状態が下の3つの文言のカードを「受付中」として通す
  ・parse_when_row: そのカードは販売期間がHTMLに無い（when=''）ので、締切の代わりに公演日を date にする
    （既存の印付きの枠と同じ形＝例 id2593「一般発売（北海道 11/9公演）」date=公演日）
印（pia_mark_soldout_slots.py と同じ付け方）:
  予定枚数終了          → soldout:true
  販売終了／抽選受付終了 → soldout:true ＋ saleEnded:true（期間切れ＝弱いほうに倒す）
それ以外の文言（中止・延期・貸切など）は通さない＝入れない。
出力: tmp/x0922/built_onsale_027_sold.json（1候補＝1URL・各ticketに url を付ける）
"""
import datetime, io, json, sys
sys.path.insert(0, 'tools')
import build_pia_entries as B
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
MARK = {'予定枚数終了': 'SO', '販売終了': 'SE', '抽選受付終了': 'SE'}
SKIP_KEEP = set(int(x) for x in io.open('tmp/x0922/sold_ids_027.txt').read().split(','))

_orig_parse = B.parse_cards
_orig_when = B.parse_when_row
unknown = []


def parse_cards(h):
    rows = _orig_parse(h)
    for r in rows:
        if r['state'] in ('受付中', '発売前'):
            continue
        end = r.get('perf_end') or r.get('perfdate') or ''
        if not end or end < TODAY:
            continue
        mk = MARK.get(r.get('stt'))
        if mk:
            r['state'] = '受付中'
            r['_mark'] = mk
        else:
            unknown.append((r.get('stt'), r.get('perfdate'), r.get('title')))
    return rows


def parse_when_row(r):
    if r.get('_mark'):
        return '§' + r['_mark'] + '§', r['perfdate'], None
    return _orig_when(r)


B.parse_cards = parse_cards
B.parse_when_row = parse_when_row

cands = [c for c in json.load(io.open('tmp/x0922/cands_onsale_027.json', encoding='utf-8')) if c['newid'] in SKIP_KEEP]
out = []
for c in cands:
    e = B.build(c)
    if not e:
        print('skip', c['newid'], c['artist']); continue
    for t in e['tickets']:
        typ = t['type']
        t.setdefault('url', e['links']['pia'])
        if '§SO§' in typ:
            t['type'] = typ.replace('§SO§', '')
            t['soldout'] = True; t['soldoutSince'] = TODAY
        elif '§SE§' in typ:
            t['type'] = typ.replace('§SE§', '')
            t['soldout'] = True; t['saleEnded'] = True
            t['soldoutSince'] = TODAY; t['saleEndedSince'] = TODAY
        else:
            t['_alive'] = True      # 買える枠が混じっていたら目立たせる（今回は無いはず）
    out.append(e)
    print(c['newid'], e['name'][:34], '枠%d' % len(e['tickets']),
          'SO%d' % sum(1 for t in e['tickets'] if t.get('soldout') and not t.get('saleEnded')),
          'SE%d' % sum(1 for t in e['tickets'] if t.get('saleEnded')))
json.dump(out, io.open('tmp/x0922/built_onsale_027_sold.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('unknown文言', unknown)
print('DROPPED', B._DROPPED)
