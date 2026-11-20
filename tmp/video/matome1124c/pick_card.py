# -*- coding: utf-8 -*-
# タップ場面のカード候補＝歌った組のうち 11/6 発売の受付を持つカード（読むだけ）
import io, json, re
R = 'C:/Users/user/oshinavi/'
s = io.open(R + 'index.html', encoding='utf-8').read()
i = s.index('const EVENTS = [') + len('const EVENTS = ')
E, _ = json.JSONDecoder().raw_decode(s[i:])
NAMES = ['ピース 又吉直樹', 'さや香', 'コットン', 'レイザーラモン', 'ニッポンの社長']
out = []
for e in E:
    if e.get('genre') == 'new':
        continue
    arts = [x.strip() for x in re.split(r'[／/]', e.get('artist') or '')]
    if not any(n in arts for n in NAMES):
        continue
    ts = [t for t in e.get('tickets') or [] if t.get('startDate') == '2026-11-06']
    if not ts:
        continue
    out.append('%s ｜ %s ｜ %s ｜ %s ｜ 受付%d' % (e['id'], e.get('name'), e.get('artist'), e.get('dateLabel'), len(e.get('tickets') or [])))
    for t in ts:
        out.append('    %s ｜ %s ｜ date %s ｜ %s' % (t.get('type'), t.get('url'), t.get('date'), 'soldout' if t.get('soldout') else ''))
io.open(R + 'tmp/video/matome1124c/pick_card.txt', 'w', encoding='utf-8').write('\n'.join(out))
