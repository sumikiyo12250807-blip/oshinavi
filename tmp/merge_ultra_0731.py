# -*- coding: utf-8 -*-
"""7/31 ユーザー指示の仕上げ2件。

(1) id3510 第39期竜王戦第2局三島対局 前夜祭 → genre=dento + extraGenres=["sports"]（ユーザー「伝統とスポーツ」）
(2) id3515 ウルトラヒーローズ THE LIVE（楽天版）を id2544（ぴあ版・kids）へ統合して 3515 を削除
    （ユーザー「キッズ・まとめて」）

統合の考え方:
  - 楽天7枠はすべて残す（会場別の楽天URLを ticket.url に付与＝バッジから直接その会場の売り場へ）
  - ぴあ4枠のうち、岐阜9/12・兵庫9/26 は楽天と販売日・締切が完全一致＝重複なので楽天枠に集約
    （[[feedback_tour_badge_split_by_saledate]] 同一販売日+種別は1バッジ）
  - ぴあの宮城11/1(8/22発売)・千葉11/14(9/5発売) は楽天より遅い**別プレイガイドの別受付**＝
    買える枠なので落とさず「ぴあ一般発売…」として残す（[[feedback_capture_all_deadlines_on_add]]）
  - links は rakuten（収益源・最優先）＋ pia（bundle）を両方保持

CRLF保護＝読みは universal newlines、書きは text モード。
  python tmp/merge_ultra_0731.py          # プランだけ
  python tmp/merge_ultra_0731.py --apply  # 適用
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

RAK_T = 'https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl=https%3A%2F%2Fticket.rakuten.co.jp%2Fevent%2F{}%2F'
RAK = RAK_T.format
PIA_BUNDLE = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669140'

# 統合後の tickets（date 昇順）
MERGED = [
    {"type": "楽天チケット2次先行（宮城 11/1公演）〜8/2 23:59",
     "date": "2026-08-02", "url": RAK('rtntuti')},
    {"type": "楽天チケット最速先行（千葉 11/14公演）8/1 10:00発売 〜8/4 23:59",
     "date": "2026-08-04", "startDate": "2026-08-01", "url": RAK('rtntuts')},
    {"type": "楽天チケット2次先行（千葉 11/14公演）8/8 10:00発売 〜8/16 23:59",
     "date": "2026-08-16", "startDate": "2026-08-08", "url": RAK('rtntuts')},
    {"type": "一般発売（岐阜 9/12公演）〜9/11 23:59",
     "date": "2026-09-11", "url": RAK('rtntutg')},
    {"type": "一般発売（兵庫 9/26公演）〜9/25 23:59",
     "date": "2026-09-25", "url": RAK('rtntuth')},
    {"type": "一般発売（宮城 11/1公演）8/8 10:00発売 〜10/31 23:59",
     "date": "2026-10-31", "startDate": "2026-08-08", "url": RAK('rtntuti')},
    {"type": "一般発売（千葉 11/14公演）8/22 10:00発売 〜11/13 23:59",
     "date": "2026-11-13", "startDate": "2026-08-22", "url": RAK('rtntuts')},
    # ↓ぴあ側の別受付（楽天より遅い一般発売）＝落とさず残す
    {"type": "ぴあ一般発売（宮城 11/1公演）8/22 10:00発売",
     "date": "2026-08-22", "startDate": "2026-08-22", "url": PIA_BUNDLE},
    {"type": "ぴあ一般発売（千葉 11/14公演）9/5 10:00発売",
     "date": "2026-09-05", "startDate": "2026-09-05", "url": PIA_BUNDLE},
]
MERGED.sort(key=lambda t: t['date'])

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
if not m:
    raise SystemExit('EVENTS が見つからない')
EVENTS = json.loads(m.group(2))

src = next((e for e in EVENTS if e['id'] == 3515), None)
dst = next((e for e in EVENTS if e['id'] == 2544), None)
ryu = next((e for e in EVENTS if e['id'] == 3510), None)
if not (src and dst and ryu):
    raise SystemExit('対象エントリが揃わない')

print('--- (1) id=3510 %s' % ryu['name'])
print('    genre: %s(_genre=%s) → dento + extraGenres=["sports"]' % (ryu['genre'], ryu.get('_genre')))

print('--- (2) 統合 id=3515 → id=2544')
print('    2544 現在 %d枠 / 3515 現在 %d枠 → 統合後 %d枠' % (len(dst['tickets']), len(src['tickets']), len(MERGED)))
for t in MERGED:
    tag = 'ぴあ' if t['url'] == PIA_BUNDLE else '楽天'
    print('      [%s] %-52s date=%s' % (tag, t['type'], t['date']))
print('    links: pia=維持 / rakuten=3515から引継ぎ')

if not APPLY:
    print('\n(プランのみ。適用は --apply)')
    raise SystemExit(0)

# (1) 竜王戦
ryu['genre'] = 'dento'
ryu['extraGenres'] = ['sports']
for k in ('_genre', '_extraGenres', '_piaSub'):
    ryu.pop(k, None)

# (2) 統合
dst['tickets'] = MERGED
dst['links']['rakuten'] = src['links']['rakuten']
dst['verifiedAt'] = '2026-07-31'
EVENTS[:] = [e for e in EVENTS if e['id'] != 3515]

# 検算
left = [e['id'] for e in EVENTS if e.get('genre') == 'new']
if left:
    raise SystemExit('genre:new が残っている: %s' % left)
resid = [e['id'] for e in EVENTS if any(k in e for k in ('_genre', '_extraGenres', '_piaSub'))]
if resid:
    raise SystemExit('下書きフィールドが残っている: %s' % resid[:10])
if any(e['id'] == 3515 for e in EVENTS):
    raise SystemExit('3515 が消えていない')

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

mo = re.search(r'(const\s+NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
if not mo:
    raise SystemExit('NEW_ORDER が見つからない')
body = body[:mo.start()] + mo.group(1) + '[]' + body[mo.end():]

open('index.html.bak_0731_merge_ultra', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
print('\n=== 適用 / 総エントリ %d件 / NEW_ORDER=[] / backup=index.html.bak_0731_merge_ultra ===' % len(EVENTS))
