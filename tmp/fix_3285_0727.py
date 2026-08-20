# -*- coding: utf-8 -*-
"""ルシファー吉岡(3285)のバッジ県に北海道を足す。
   ぴあの県リストが「東京都／大阪府」しか持っておらず、券種名〔東京・大阪・北海道〕と食い違っていた。
   裏取り＝お笑いナタリー「初の大阪や北海道での公演も」＋10/25 北海道カタリナスタジオ。
   使い方: python tmp/fix_3285_0727.py [--apply]
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
OLD, NEW = '（東京・大阪 9/21〜10/25公演）', '（東京・大阪・北海道 9/21〜10/25公演）'

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 3285)
assert e['name'] == 'ルシファー吉岡ネタライブ2026', e['name']

n = 0
for t in e['tickets']:
    if OLD in t['type']:
        print('  旧:', t['type'])
        t['type'] = t['type'].replace(OLD, NEW)
        print('  新:', t['type'])
        n += 1
print(f'\n{n}枠を書き換え（会場: {e["venue"]}）')
assert n == len(e['tickets']), '全枠が対象のはず'

if not apply:
    print('(--apply で書き込み)')
    sys.exit(0)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
print('書き込み完了')
