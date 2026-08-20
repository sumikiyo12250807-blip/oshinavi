# -*- coding: utf-8 -*-
"""ドラクエ アイランドの4分割を id2823 に統合する（2824/2825/2957 は delete_entries で別途削除）。
   券種名はビルダーが落とすので、各ページの公演名から復元して枠を区別できるようにする
   （memory: feedback_newpool_fullwidth_halfwidth の「席名ラベルを復元して区別する（消さない）」）。
   CRLF を壊さない（memory: feedback_index_html_crlf_preserve）。
   使い方: python tmp/dq_apply_0727.py [--apply]
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
BASE = '一般発売（兵庫 7/27〜12/31公演）〜12/29 23:59'
KENSHU = [  # (券種名, eventCd)  ※元の4エントリの公演名から採った
    ('ライトチケット', '2628477'),
    ('ゴールドチケット', '2628482'),
    ('プレミアムチケット', '2628483'),
    ('プレミアムオールインワンチケット', '2628484'),
]

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
assert m, 'EVENTS配列が見つからない'
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

# 統合前に、消す3件が本当に同じ興行か（会場・期間・締切が一致するか）を機械確認する
keep = by_id[2823]
for eid in (2824, 2825, 2957):
    o = by_id[eid]
    assert o['venue'] == keep['venue'], f'id{eid} 会場が違う'
    assert o['date'] == keep['date'], f'id{eid} 公演期間が違う'
    assert [t['date'] for t in o['tickets']] == [t['date'] for t in keep['tickets']], f'id{eid} 締切が違う'
print('同一興行チェック: 会場・期間・締切すべて一致 OK')

keep['artist'] = 'ドラゴンクエスト アイランド'
keep['name'] = 'ドラゴンクエスト アイランド'
keep['genre'] = 'art'          # 兄弟(ゴジラ/NARUTO/クレヨンしんちゃん)に合わせる
keep['tickets'] = [
    {'type': f'{k} {BASE}', 'date': '2026-12-29',
     'url': f'https://t.pia.jp/pia/event/event.do?eventCd={cd}'}
    for k, cd in KENSHU
]
keep['verifiedAt'] = '2026-07-27'

print('\n=== 統合後の id2823 ===')
print(' name  :', keep['name'])
print(' genre :', keep['genre'])
for t in keep['tickets']:
    print('  枠:', t['type'])
    print('      ', t['url'])
print('\n削除する: 2824 / 2825 / 2957')

if not apply:
    print('\n(--apply で書き込み)')
    sys.exit(0)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start(2)] + dumped + src[m.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('\n書き込み完了（2824/2825/2957 の削除は delete_entries.py で）')
