# -*- coding: utf-8 -*-
"""振り分け前の下書き(_genre/_extraGenres)補正。index.htmlのCRLFを壊さない。
   memory: feedback_index_html_crlf_preserve
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
FIX = {
    # id: (_genre, _extraGenres, 理由)
    3222: ('hanabi', None, '下書き空＝花火大会'),
    3227: ('engeki', None, '下書き空＝作家×トーク/朗読型。既存の同型16件がengeki'),
    3229: ('hanabi', None, '下書き空＝花火大会'),
    3233: ('kids', None, '下書き空＝3歳以上有料の子ども向け・140cm未満は立って鑑賞'),
    3231: ('dinnershow', None, 'engekiを訂正＝Breakfast Show/Dinner Show(食事付き)'),
    3243: ('classic', ['engeki'], 'バレエ＝classic+engeki(2026-06-20ユーザー確定)'),
    3247: ('classic', ['engeki'], 'バレエ＝classic+engeki(2026-06-20ユーザー確定)'),
}

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
assert m, 'EVENTS配列が見つからない'
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

for eid, (g, extra, why) in FIX.items():
    e = by_id.get(eid)
    if e is None:
        print(f'  id{eid} が見つからない')
        continue
    if e.get('genre') != 'new':
        print(f'  id{eid} は genre:new でない（{e.get("genre")}）→ スキップ')
        continue
    old = e.get('_genre') or '（空）'
    e['_genre'] = g
    if extra:
        e['_extraGenres'] = extra
    print(f"  id{eid} {old} → {g}{'+' + '+'.join(extra) if extra else ''}  ({why})")

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start(2)] + dumped + src[m.end(2):]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
