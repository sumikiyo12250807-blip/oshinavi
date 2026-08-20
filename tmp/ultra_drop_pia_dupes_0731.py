# -*- coding: utf-8 -*-
"""id2544 ウルトラヒーローズ：ぴあ由来の重複2枠を外して楽天7枠に寄せる。

理由:
  - 宮城11/1・千葉11/14 の「一般発売」は楽天(8/8・8/22発売)とぴあ(8/22・9/5発売)の
    同じ公演・同じ販売波。楽天の方が2週間早く買えるので、ぴあ枠を出しても
    「新しく買えるようになる日」ではない＝カウントダウン価値がない。
  - ぴあ枠は締切未掲出(startDate==date)＝隠れ枠になり毎朝のヒール対象が増える。
  - ぴあでも扱いがある事実は links.pia として残す（枠は落とすがリンクは落とさない）。
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
e = next(x for x in EVENTS if x['id'] == 2544)

keep = [t for t in e['tickets'] if not t['type'].startswith('ぴあ')]
drop = [t for t in e['tickets'] if t['type'].startswith('ぴあ')]
print('残す %d枠 / 外す %d枠' % (len(keep), len(drop)))
for t in drop:
    print('  外す: %s' % t['type'])
for t in keep:
    print('  残す: %s' % t['type'])

if not APPLY:
    print('\n(プランのみ。適用は --apply)')
    raise SystemExit(0)

e['tickets'] = keep
assert e['links'].get('pia'), 'ぴあリンクが消えている'
assert e['links'].get('rakuten'), '楽天リンクが消えている'

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html.bak_0731_ultra_pia_dupes', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(body)
print('\n=== 適用 / 2544 は %d枠 / backup=index.html.bak_0731_ultra_pia_dupes ===' % len(keep))
