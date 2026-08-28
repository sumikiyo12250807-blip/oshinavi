# -*- coding: utf-8 -*-
"""ヒールの安全弁で止まった5件を、実ページを1件ずつ見て手で当てる（2026-08-28 昼）。

裏取り（ぴあ実ページ・全部この日に取得）:
  799  三山ひろし 茨城11/19  eventCd=2626936 → [受付中] 〜2026/11/15 23:59
  3040 山崎ハコ 神奈川11/3   eventCd=2611126 → [受付中] 〜2026/11/1 23:59
  1060 三遊亭兼好 視聴券     b2670035       → [受付中] 〜2026/9/26 10:00
  1863 京都市響 京都11/21    eventCd=2533286 → 🚨「この公演は予定枚数を終了いたしました」＝即完
  1095 星屑の会 北海道11/9   eventCd=2617371 → この券種はもう出ていない（宮城10/25だけが受付中）

🚨 index.html は CRLF。json.dumps の LF を元の改行へ戻す。
"""
import io, re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
PATH = 'index.html'
src = io.open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src[:4000] else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
E = json.loads(m.group(2))
by = {e['id']: e for e in E}

def patch(eid, match, **kw):
    e = by[eid]
    hit = 0
    for t in (e.get('tickets') or []):
        if match in (t.get('type') or ''):
            for k, v in kw.items():
                if v is None:
                    t.pop(k, None)
                else:
                    t[k] = v
            hit += 1
            print('  id%-5s %s → %s' % (eid, t['type'][:52], {k: v for k, v in kw.items()}))
    assert hit == 1, 'id%d の対象が%d件' % (eid, hit)

print('=== 締切を当てる ===')
patch(799,  '一般発売（茨城 11/19公演）',  type='一般発売（茨城 11/19公演）〜11/15 23:59', date='2026-11-15', startDate=None)
patch(3040, '一般発売（神奈川 11/3公演）', type='一般発売（神奈川 11/3公演）〜11/1 23:59', date='2026-11-01', startDate=None)
patch(1060, '【動画配信】（全国 9/12〜9/26公演）',
      type='一般発売【視聴券】【動画配信】（全国 9/12〜9/26公演）〜9/26 10:00', date='2026-09-26', startDate=None)

print('=== 予定枚数終了にする（即完） ===')
patch(1863, '一般発売（京都 11/21公演）',
      type='一般発売（京都 11/21公演）', date='2026-11-21', startDate=None,
      soldout=True, soldoutSince=TODAY,
      url='https://t.pia.jp/pia/ticketInformation.do?eventCd=2533286&rlsCd=001')

print('=== 販売終了にする（ぴあに券種が残っていない） ===')
patch(1095, '一般発売（北海道 11/9公演）',
      type='一般発売（北海道 11/9公演）', date='2026-11-09', startDate=None,
      soldout=True, saleEnded=True, saleEndedSince=TODAY)

io.open(PATH, 'w', encoding='utf-8', newline='').write(
    src[:m.start(2)] + json.dumps(E, ensure_ascii=False, indent=2).replace('\n', nl) + src[m.end(2):])
print('書き戻した')
