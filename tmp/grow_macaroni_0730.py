"""id3484 マカロニえんぴつを「北海道1公演だけ」→ ぴあにある全公演のツアー1エントリに育てる。
ユーザー指摘（2026-07-30）「いっぱいあるよ／他にもあるんじゃない？全国ツアー」。
真因＝harvestは既存artist名で除外するので同名の別公演を永久に拾えない
（[[feedback_harvest_name_dedup_blindspot]]）。tools/pia_kw_search.py で3ページ発見:
  2620662 福岡 マリンメッセ福岡A館 10/24-25 ／ 2621851 北海道 真駒内 10/31(登録済) ／
  2614402 東京 有明アリーナ11/3・国立代々木12/5-6
ツアーは1エントリにまとめる（[[feedback_tour_consolidate]]）・各枠に会場別URL（[[feedback_tour_per_ticket_url]]）。
新着プールなので **id据え置きの現物編集**（[[feedback_new_list_order_lock]]）。

  python tmp/grow_macaroni_0730.py            # 差分表示のみ
  python tmp/grow_macaroni_0730.py --apply
"""
import json
import re
import sys

APPLY = '--apply' in sys.argv
TARGET = 3484

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
cur = byid[TARGET]
# PowerShellのリダイレクトでBOM付きになるので utf-8-sig で読む
new = json.load(open('tmp/built_macaroni.json', encoding='utf-8-sig'))[0]
assert new['id'] == TARGET, 'ビルド結果のidが違う'

out = ['id%d %s' % (TARGET, cur.get('artist'))]
for k in ('date', 'dateLabel', 'venue', 'prefecture'):
    out.append('  %-11s 現在: %s' % (k, cur.get(k)))
    out.append('  %-11s 新規: %s' % ('', new.get(k)))
out.append('  links.pia 現在: %s' % (cur.get('links') or {}).get('pia'))
out.append('  links.pia 新規: %s' % (new.get('links') or {}).get('pia'))
out.append('  枠 %d → %d' % (len(cur.get('tickets') or []), len(new['tickets'])))
out.append('  --- 現在の枠 ---')
for t in cur.get('tickets') or []:
    out.append('    %s | date=%s start=%s url=%s' % (t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))
out.append('  --- 新しい枠（ぴあ3ページから再導出）---')
for t in new['tickets']:
    out.append('    %s | date=%s start=%s url=%s' % (t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))

# 消える枠に非ぴあURLが無いか（楽天/e+枠を巻き込まない安全確認）
def key(t):
    return (t.get('type') or '', t.get('date') or '')
newk = {key(t) for t in new['tickets']}
lost = [t for t in (cur.get('tickets') or []) if key(t) not in newk]
nonpia = [t for t in lost if t.get('url') and 'pia.jp' not in t['url']]
out.append('  消える枠 %d件 / うち非ぴあ %d件%s' % (len(lost), len(nonpia), '  🚨適用中止' if nonpia else ''))
assert not nonpia, '非ぴあ枠が消える＝中止'

if APPLY:
    cur['tickets'] = new['tickets']
    for k in ('date', 'dateLabel', 'venue', 'prefecture'):
        cur[k] = new[k]
    cur['links']['pia'] = new['links']['pia']
    cur['verifiedAt'] = new['verifiedAt']
    open('index.html.bak_0730_macaroni', 'w', encoding='utf-8').write(h)
    # CRLF保護＝読みは universal newlines・書きは text モード（newline='' を使わない）
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    out.append('=== 適用した (backup: index.html.bak_0730_macaroni) ===')
else:
    out.append('=== 表示のみ。適用するなら --apply ===')

open('tmp/grow_macaroni_0730.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/grow_macaroni_0730.txt apply=%s' % APPLY)
