# -*- coding: utf-8 -*-
"""同じ文言のバッジが並んでいた5件を、見分け札つきで作り直した結果に差し替える（2026-08-22）。

対象＝1128 ニッチェ／2175 花冷え。／2990 森高千里／4052 LiSA／4114 Yung Kai。
build_pia_entries に入れた disambiguate() が、会場名・券種名の差分から札を付けてくれる。

差し替えるのは**ぴあ由来の枠だけ**。次は残す（[[feedback_soldout_keep_visible]]／
[[feedback_delete_nonpia_blindspot]]）：
  ① soldout / saleEnded が付いた枠（予定枚数終了は消さない）
  ② ぴあ以外の売り場（e+／ローチケ／楽天）の枠
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

built = {e['id']: e for e in json.load(open('tmp/dup_built_0822.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

log = io.open('tmp/dup_apply_0822.txt', 'w', encoding='utf-8')
for e in EVENTS:
    b = built.get(e['id'])
    if not b:
        continue
    old = e.get('tickets') or []
    keep = [t for t in old
            if t.get('soldout') or t.get('saleEnded')
            or (t.get('url') and 'pia.jp' not in t['url'])]
    have = {t['type'] for t in b['tickets']}
    newt = list(b['tickets']) + [t for t in keep if t['type'] not in have]
    log.write('== id%-5d %s : 枠 %d → %d\n' % (e['id'], e.get('name', ''), len(old), len(newt)))
    for t in old:
        if t['type'] not in {x['type'] for x in newt}:
            log.write('   - 落とす（ぴあの買える枠でなくなった）: %s | %s\n' % (t['type'], t.get('date')))
    for t in newt:
        if t['type'] not in {x['type'] for x in old}:
            log.write('   + %s | %s\n' % (t['type'], t.get('date')))
    if APPLY:
        e['tickets'] = newt
        e['verifiedAt'] = '2026-08-22'
log.close()
print('→ tmp/dup_apply_0822.txt')

if APPLY:
    shutil.copyfile('index.html', 'index.html.bak_0822_dup')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2)
        + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（判定のみ。適用は --apply）')
