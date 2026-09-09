# -*- coding: utf-8 -*-
"""ぴあ以外の新着22件だけを振り分けるための準備。

・id7498 の下書きジャンルを musicetc にする（2026-09-10 ユーザー決定
  「7498はmusicetcで」＝楽天のURLが /event/ だけでジャンルの手がかりが無かった分）
・振り分け対象は**ユーザーが目視で確認した22件だけ**。
  今日入れた分（ぴあ95件＋OZ＋吉幾三＋星影の人）は**翌朝の再チェックのあと**なので外す。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ユーザーが「今乗ってる楽天チケットは目視で確認できた」と言った時点でタブにあった分
OK = [7492, 7493, 7494, 7495, 7496, 7497, 7498, 7499, 7500, 7501, 7502, 7503,
      7504, 7505, 7506, 7507, 7582, 7583, 7584, 7585, 7706, 7707]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

for e in events:
    if e['id'] == 7498:
        print('id=7498 %s : _genre %r → musicetc' % (e['name'][:30], e.get('_genre')))
        e['_genre'] = 'musicetc'

pool = [e['id'] for e in events if e.get('genre') == 'new']
skip = sorted(set(pool) - set(OK))
print('新着プール %d件 / 振り分ける %d件 / 残す %d件'
      % (len(pool), len([i for i in pool if i in OK]), len(skip)))
print('--exclude %s' % ','.join(str(i) for i in skip))

if '--apply' not in sys.argv:
    print('(--apply で _genre だけ先に書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
io.open('tmp/assign_exclude_0910.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in skip))
print('書き込み完了 → tmp/assign_exclude_0910.txt')
