# -*- coding: utf-8 -*-
"""新着チェックで見つかった実害を直す（現物編集・id据え置き）。

① id3508 THE AWAODORI
   a. 直したビルダーで作り直し＝【8／13（木）第2部】が復活（同じ会場の2枠が同じバッジだった）
   b. EXCLUSIVE SEAT の2枠は ぴあのタイトルが ＜EXCLUSIVE SEAT…＞ と省略記号で切れており、
      券種名(「個人向け二次抽選受付(1-4名様用)」「グループ向け二次抽選受付（最大5名様用）」)が
      落ちて**バッジに「...」が生で出て、個人用とグループ用の区別が消えていた**。
      実ページの文言で手当てする（機械では取れない形＝ここだけ手作業）。
② id3470/3503 Amazonリンクのクエリ差し替え（実測ベース）
   3470 「デビュー35周年記念 横山幸雄ピアノ・リサイタル…CD」→ 0件同然 → 「横山幸雄」で10件
        ※amazon_audit の自動短縮は「デビュー35」を出してきたが、当たった11件は別人のCD＝却下
   3503 「九州交響楽団 第444回定期演奏会 CD」→ 「九州交響楽団」で9件
   クラシックの団体/演奏家は「CD」語を付けない方が当たる（ユーザー確認済のルール）
"""
import json
import re
import sys
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import build
import reconcile_pia as R

h = open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
log = []

# ---- ① 3508 ----
e = byid[3508]
ne = build({'newid': 3508, 'artist': e.get('artist', ''), 'urls': R.pia_urls(e)})
assert ne is not None, '3508 が買える枠ゼロで返ってきた'
tickets = ne['tickets']
EXC = {
    'EXCLUSIVE SEAT...': '先行【EXCLUSIVE SEAT 個人向け二次抽選 1-4名様】',
    'EXCLUSIVE...': '先行【EXCLUSIVE SEAT グループ向け二次抽選 最大5名様】',
}
n_exc = 0
for t in tickets:
    mm = re.match(r'先行【(EXCLUSIVE[^】]*)】', t['type'])
    if mm and mm.group(1) in EXC:
        old = t['type']
        t['type'] = EXC[mm.group(1)] + t['type'][mm.end():]
        n_exc += 1
        log.append(f'  枠: {old}')
        log.append(f'   → {t["type"]}')
assert n_exc == 2, f'EXCLUSIVE枠が {n_exc} 件しか当たっていない（2件のはず）'
dup = [k for k in {t['type'] for t in tickets} if [x['type'] for x in tickets].count(k) > 1]
assert not dup, f'同一バッジが残っている: {dup}'
e['tickets'] = tickets
log.insert(0, f'id=3508 THE AWAODORI  枠{len(tickets)}件を作り直し＋EXCLUSIVE2枠を手当て')

# ---- ② Amazonクエリ ----
AMZ = {3470: '横山幸雄', 3503: '九州交響楽団'}
for i, kw in AMZ.items():
    ev = byid[i]
    old = (ev.get('links') or {}).get('amazon') or ''
    assert old, f'id={i} に amazonリンクが無い'
    new = ('https://www.amazon.co.jp/s?k=' + urllib.parse.quote(kw)
           + '&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22')
    ev['links']['amazon'] = new
    oldq = urllib.parse.parse_qs(urllib.parse.urlparse(old).query).get('k', [''])[0]
    log.append('')
    log.append(f'id={i} {(ev.get("artist") or "")[:44]}')
    log.append(f'  Amazonクエリ 「{oldq}」 → 「{kw}」（CD語なし）')

open('index.html.bak_0730_newfix', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
log.append('')
log.append('=== 3件修正 (backup: index.html.bak_0730_newfix) ===')
open('tmp/fix_new48_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('wrote tmp/fix_new48_0730.txt')
