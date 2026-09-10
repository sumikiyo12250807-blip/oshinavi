# -*- coding: utf-8 -*-
"""ログイン済みブラウザで読んだフォロワー実数を tools/x_log.json に貯める。

🚨WebSearchでは1件も取れなかったが、**x.com のプロフィールを開けば全部読める**
（[[reference_x_follower_lookup]] の2026-08-18訂正どおり）。
今回それを実地でやり直した＝落語家・中堅バンドは検索に出ないので**ブラウザが正**。
"""
import io
import json

p = 'tools/x_log.json'
d = json.load(io.open(p, encoding='utf-8'))
arts = d['artists']['data']
idx = {a['name']: a for a in arts}

MEASURED = [
    ('ズーカラデル', '@gooutzoo', 34000,
     '34K。2026-09-10 ブラウザで実測'),
    ('鳥肌実', '@Kotori_Co', 23000,
     '23K。**ことり事務所が運営する公式**（本人垢ではない）。2026-09-10 ブラウザで実測'),
    ('桂米團治', '@yonedanji_k', 9185,
     '2026-09-10 ブラウザで実測'),
    ('ナナクロニクル', '@info_7chronicle', 5456,
     '公式。2026-09-10 ブラウザで実測'),
    ('柳家喬太郎', None, None,
     '🚨本人アカウント無し（botとファン垢だけ）。2026-09-10 ブラウザで確認'),
    ('桂二葉', None, None,
     '🚨本人アカウント無し（応援団「によによ団」だけ）。2026-09-10 ブラウザで確認'),
    ('寺尾聰', None, None,
     '🚨本人アカウント無し（「本物」を名乗る垢はあるが確証なし・偽垢多数）。2026-09-10 確認'),
    ('キム・チャンワンバンド', None, None,
     '🚨Xに김창완 밴드のアカウントが無い。2026-09-10 確認'),
]

for name, handle, fol, note in MEASURED:
    a = idx.get(name)
    if a:
        a['handle'] = handle
        a['followers'] = fol
        a['note'] = note
        print('更新: %-16s %s' % (name, fol if fol else '本人アカウント無し'))
    else:
        arts.append({'name': name, 'handle': handle, 'followers': fol, 'note': note})
        print('追加: %-16s %s' % (name, fol if fol else '本人アカウント無し'))

# 野村萬斎・春風亭昇太は既にあるので note を実測で上書き
if '野村萬斎' in idx:
    idx['野村萬斎'].update({'handle': '@mansai_gozaru', 'followers': 19300,
                        'note': '19.3K。**本人でなく主宰する狂言会「狂言ござる乃座」の公式**。2026-09-10 実測'})
    print('更新: 野村萬斎           19300')
if '春風亭昇太' in idx:
    idx['春風亭昇太'].update({'handle': None, 'followers': None,
                         'note': '🚨本人アカウント無し。@syoten1erai は203フォロワー・104ポストで'
                                 '2019年止まり＝本人ではない。2026-09-10 ブラウザで確認'})
    print('更新: 春風亭昇太          本人アカウント無し')

d['artists']['measured'] = '2026-09-10'
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('')
print('tools/x_log.json を更新（artists %d件）' % len(arts))
