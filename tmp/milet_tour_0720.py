# -*- coding: utf-8 -*-
"""milet の既存エントリ(id2188・札幌単独)を ツアー1エントリに育てる。

背景:
  milet live tour 2026「Made of Glass」は全国17都市19公演だが、OSHINAVIには
  ぴあで拾えた札幌11/13の1件しか無かった（ぴあのartistsページを総ざらいして
  他公演がぴあに無いことを確認済み＝関連枠6件は全部別アーティストだった）。
  ローチケ扱い9公演は l-tike.com が機械アクセスを弾くため
  （[[reference_ltike_machine_unreachable]]）、ユーザーが画面から読み上げてくれた分を登録する。

🚨 受付期間は公演ごとにバラバラだった（一律だと決めつけない）:
  仙台10/24・福島10/25 → 7/10(金)12:00 〜 7/26(日)23:59 / 抽選結果 7/29 15:00頃
  大阪11/1・11/2       → 7/9(木)12:00 〜 **7/20(月)23:59**（本日締切のため登録しない。
                          今から入れても公開は明日＝締切後になる）
  京都/愛知/札幌/福岡/大分 → **未確認。分かるまで登録しない**（[[feedback_no_placeholder_dates]]）

ツアー名は milet 本人の公式X「ツアータイトル決定！」で裏取り済み。
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

LTIKE_SENDAI = ('https://l-tike.com/order/?gLcode=52407&gPfKey=20260204000002133207,20260204000002133206'
                '&gEntryMthd=03&gScheduleNo=4&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
                '&gBaseVenueCd=53674')
LTIKE_FUKUSHIMA = ('https://l-tike.com/order/?gLcode=23176&gPfKey=20260204000002133242'
                   '&gEntryMthd=03&gScheduleNo=2&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
                   '&gBaseVenueCd=24638')
LTIKE_AICHI = ('https://l-tike.com/order/?gLcode=41759&gPfKey=20260204000002133152'
               '&gEntryMthd=03&gScheduleNo=4&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
               '&gBaseVenueCd=46895')
LTIKE_OSAKA = ('https://l-tike.com/order/?gLcode=52407&gPfKey=20260204000002133205'
               '&gEntryMthd=03&gScheduleNo=4&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
               '&gBaseVenueCd=59997')
LTIKE_FUKUOKA = ('https://l-tike.com/order/?gLcode=93281&gPfKey=20260204000002133277'
                 '&gEntryMthd=03&gScheduleNo=4&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
                 '&gBaseVenueCd=84423')
LTIKE_OITA = ('https://l-tike.com/order/?gLcode=93281&gPfKey=20260204000002133278'
              '&gEntryMthd=03&gScheduleNo=4&gCarrierCd=01&gPfName=%EF%BD%8D%EF%BD%89%EF%BD%8C%EF%BD%85%EF%BD%94'
              '&gBaseVenueCd=88097')
PIA_SAPPORO = 'https://t.pia.jp/pia/event/event.do?eventCd=2616603'

NAME = 'milet live tour 2026「Made of Glass」'
VENUE = ('全国ツアー（仙台サンプラザホール／とうほう・みんなの文化センター／フェスティバルホール／'
         'Niterra日本特殊陶業市民会館 フォレストホール／札幌文化芸術劇場hitaru／福岡サンパレス／'
         'iichikoグランシアタ）')
DATELABEL = ('2026年10月24日(土)〜2026年11月22日(日) 全国ツアー '
             '仙台サンプラザホール／とうほう・みんなの文化センター／フェスティバルホール／'
             'Niterra日本特殊陶業市民会館 フォレストホール／札幌文化芸術劇場hitaru／福岡サンパレス／'
             'iichikoグランシアタ')

# 🚨 受付期間は公演ごとにバラバラ。全部ユーザーが実画面で1件ずつ読み上げて確認したもの。
#    7/9〜7/20(本日締切) = 大阪・福岡・大分 ／ 7/10〜7/26 = 仙台・福島 ／ 7/14〜7/27 = 愛知
#    「同じツアーだから一律」と決めつけていたら大阪の締切を6日間まちがえて出していた。
TICKETS = [
    {'type': '抽選先行〔スマートフォン受付のみ〕（宮城 10/24公演）〜7/26 23:59',
     'date': '2026-07-26', 'startDate': '2026-07-10', 'url': LTIKE_SENDAI},
    {'type': '抽選先行〔スマートフォン受付のみ〕（福島 10/25公演）〜7/26 23:59',
     'date': '2026-07-26', 'startDate': '2026-07-10', 'url': LTIKE_FUKUSHIMA},
    {'type': '抽選先行〔スマートフォン受付のみ〕（大阪 11/1〜11/2公演）〜7/20 23:59',
     'date': '2026-07-20', 'startDate': '2026-07-09', 'url': LTIKE_OSAKA},
    {'type': '抽選先行〔スマートフォン受付のみ〕（愛知 11/8公演）〜7/27 23:59',
     'date': '2026-07-27', 'startDate': '2026-07-14', 'url': LTIKE_AICHI},
    # 既存のぴあ枠（札幌）はそのまま残し、URLだけ明示して誤誘導を防ぐ
    {'type': '6次プレリザーブ（北海道 11/13公演）7/21 11:00発売',
     'date': '2026-07-27', 'startDate': '2026-07-21', 'url': PIA_SAPPORO},
    {'type': '抽選先行〔スマートフォン受付のみ〕（福岡 11/21公演）〜7/20 23:59',
     'date': '2026-07-20', 'startDate': '2026-07-09', 'url': LTIKE_FUKUOKA},
    {'type': '抽選先行〔スマートフォン受付のみ〕（大分 11/22公演）〜7/20 23:59',
     'date': '2026-07-20', 'startDate': '2026-07-09', 'url': LTIKE_OITA},
]


def main():
    src = open(PATH, encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    events = json.loads(m.group(2))
    e = next((x for x in events if x['id'] == 2188), None)
    assert e, 'id=2188 が無い'

    print('--- before ---')
    print(f'  name={e.get("name")} / venue={e.get("venue")} / pref={e.get("prefecture")}')
    print(f'  枠{len(e.get("tickets", []))}')

    e['name'] = NAME
    e['venue'] = VENUE
    e['dateLabel'] = DATELABEL
    e['prefecture'] = '全国'
    e['date'] = '2026-11-22'          # 千秋楽＝大分11/22
    e.setdefault('links', {})['lawson'] = 'https://l-tike.com/concert/mevent/?mid=488638'
    e['tickets'] = TICKETS
    e['verifiedAt'] = '2026-07-20'

    print('--- after ---')
    print(f'  name={e["name"]}')
    print(f'  venue={e["venue"]}')
    print(f'  pref={e["prefecture"]} / date={e["date"]}')
    print(f'  lawson={e["links"]["lawson"]}')
    for t in e['tickets']:
        print(f'  枠: {t["type"]}')
        print(f'      date={t["date"]} startDate={t["startDate"]}')

    if not APPLY:
        print('\n(--apply で書き込み)')
        return 0
    out = src[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2) + src[m.end(2):]
    open(PATH, 'w', encoding='utf-8').write(out)
    print('\n書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
