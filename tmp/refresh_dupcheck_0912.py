# -*- coding: utf-8 -*-
"""refresh_deadlines が「追加」する枠が、既存の枠と同じ売り場を別の書き方で指していないかを見る（読むだけ）。

refresh は「券種名＋（…公演）」の骨格で同じ枠かを見分けるので、ぴあが同じ枠を
2通りの書き方で出すと（「一般発売（札幌）（北海道 12/4公演）」と「一般発売（北海道 12/4公演）」）
別の枠と見て**追加**し、同じバッジが2つ並ぶ。
memory: feedback_capture_all_deadlines_on_add（突き合わせは券種名でなく「県・公演日・締切」）

判定＝同じエントリの既存枠に、次の3つが全部同じものがあれば「重なりの疑い」:
  ①（…公演）の中の県　②（…公演）の中の公演日　③発売日（startDate）か、無ければ締切（date）
使い方: python tmp/refresh_dupcheck_0912.py <built.json>
出力: 画面 ＋ tmp/refresh_dup_ids_0912.txt（疑いのある id）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open(sys.argv[1], encoding='utf-8-sig'))}
h = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


def key(t):
    m = re.search(r'（([^（）]*?)\s*((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)公演）', t.get('type') or '')
    if not m:
        return None
    prefs = tuple(sorted(p for p in re.split(r'[・/／]', m.group(1)) if p))
    return (prefs, m.group(2), t.get('startDate') or t.get('date'))


sus = []
for i, b in built.items():
    e = by.get(i)
    if not e:
        continue
    have_head = {head(t.get('type')) for t in e.get('tickets') or []}
    have_key = {}
    for t in e.get('tickets') or []:
        k = key(t)
        if k:
            have_key.setdefault(k, []).append(t.get('type'))
    for bt in b.get('tickets') or []:
        if head(bt.get('type')) in have_head:
            continue  # 追加ではない（上書き側）
        k = key(bt)
        if k and k in have_key:
            sus.append((i, bt.get('type'), have_key[k]))

print('追加される枠のうち、既存の枠と「県・公演日・発売日(締切)」が同じもの: %d枠' % len(sus))
for i, new, olds in sus:
    print('  id%-5s 追加: %s' % (i, new))
    for o in olds:
        print('         既存: %s' % o)
io.open('tmp/refresh_dup_ids_0912.txt', 'w', encoding='utf-8').write(
    ','.join(str(x) for x in sorted({s[0] for s in sus})))
