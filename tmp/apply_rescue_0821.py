# -*- coding: utf-8 -*-
"""バッジ0（画面に買える枠が出ない）エントリのうち、ぴあに買える枠があったものを当てる。

🚨【重要】置換ではなく **追加**。
理由＝対象はどれも全国ツアーで、既存の date はツアーの千秋楽。
ぴあの単一URLから取り直すとその1公演分しか返らないので、置換すると
date が千秋楽より前へ縮み、ツアーの情報を壊す（[[feedback_pia_bundle_hides_shows]]）。
既存の期限切れ枠は画面に出ないだけなので残しておく。

検出＝node tools/check_zero_badge.js ／ 照合＝tools/reconcile_pia.py --ids ／ 構築＝tools/build_pia_entries.py
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = {e['id']: e for e in json.load(io.open('tmp/built_0821.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    b = built.get(e['id'])
    if not b:
        continue
    old = e.get('tickets') or []
    # 同一文言＋同一URLの枠は足さない（飛び先が違えば別の売り場なので残す）
    seen = {(t.get('type'), t.get('url')) for t in old}
    add = [t for t in b['tickets'] if (t.get('type'), t.get('url')) not in seen]
    print('=== id=%d %s' % (e['id'], e.get('artist')))
    print('  枠 %d → %d / date=%s（据え置き）' % (len(old), len(old) + len(add), e.get('date')))
    for t in add:
        print('    + ', t.get('type'), '|', t.get('date'))
    if b.get('date') and b['date'] > (e.get('date') or ''):
        print('  🚨 ぴあの公演日 %s が登録の %s より後 → 要確認（今回は触らない）' % (b['date'], e.get('date')))
    e['tickets'] = old + add
    e['verifiedAt'] = '2026-08-21'
    n += 1

assert n == len(built), (n, len(built))
shutil.copyfile('index.html', 'index.html.bak_0821_rescue2')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 更新 ===' % n)
