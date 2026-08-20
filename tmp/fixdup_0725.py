# -*- coding: utf-8 -*-
"""新着の重複2組を直す。
 ① id3225 ANA presents ナーポオケラ = 既存 id1768 Na Pookela ナーポオケラ と同一興行
    → 新着を削除し、楽天リンクを既存に付ける（購入ボタンは楽天優先＝feedback_vendor_priority）
 ② id3238 【泉佐野市民割・田尻町民割】大阪芸術花火 = id3239 大阪芸術花火 の別券種
    → 3239 に枠として統合し 3238 を削除（feedback_tour_consolidate / tickets_all_expand）
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

path = 'index.html'
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
byid = {e['id']: e for e in EV}
shutil.copyfile(path, 'index.html.bak_0725_dupfix')

# ① ナーポオケラ
src, dst = byid.get(3225), byid.get(1768)
if src and dst:
    rk = (src.get('links') or {}).get('rakuten')
    if rk and not (dst.get('links') or {}).get('rakuten'):
        dst.setdefault('links', {})['rakuten'] = rk
        print('id1768 に楽天リンクを付与')
    print('id3225 を削除（id1768 と同一興行）')

# ② 大阪芸術花火（市民割を通常券エントリに枠として足す）
a, b = byid.get(3238), byid.get(3239)
if a and b:
    for t in a.get('tickets', []):
        t = dict(t)
        if '市民割' not in t['type']:
            t['type'] = '【泉佐野市民割・田尻町民割】' + t['type']
        b['tickets'].append(t)
    b['tickets'].sort(key=lambda x: (x.get('startDate') or '', x['date']))
    print('id3239 に市民割の枠を統合（枠 %d本）' % len(b['tickets']))
    print('id3238 を削除')

drop = {3225, 3238}
EV2 = [e for e in EV if e['id'] not in drop]

new_arr = json.dumps(EV2, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h2)
cur = [int(x) for x in re.findall(r'\d+', mo.group(2))]
keep = [i for i in cur if i not in drop]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            r'\g<1>[' + ', '.join(str(i) for i in keep) + ']', h2, count=1)
open(path, 'w', encoding='utf-8').write(h2)
print('総%d件 → %d件 / NEW_ORDER %d件 (backup index.html.bak_0725_dupfix)' % (len(EV), len(EV2), len(keep)))
