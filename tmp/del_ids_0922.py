# -*- coding: utf-8 -*-
"""今朝消すidの一覧を作る＝公演が終わった530件から、配信が生きている3件を外した527件。

除外3件（機械の check_expired の「📺公演終了だが買える枠あり」と、別エージェントの独立検証が
**同じ3件で一致**した）＝id1904（配信〜10/4）／id6253（視聴券〜9/25）／id13937（アーカイブ〜9/27）＋別エージェントの独立チェックで見つかった5件（id77 MeseMoa. ツアー続行／id3757 配信の販売が9/30まで／id7009 10月公演あり／id13988 11/2に延期／id14033 10/27に日程変更）
＋ id17356（新着プールの1件・公演が9/20で終わっている）を足す。

出力: tmp/del_ids_0922.txt（カンマ区切り）／tmp/del_list_0922.md（公演名＋確認用URL）
"""
import io, json, re

TODAY = '2026-09-22'
KEEP = {1904, 5587, 6253, 13482, 13937, 77, 3757, 7009, 13988, 14033}

src = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))

rows = []
for e in ev:
    d = e.get('date') or ''
    if not d or d >= TODAY:
        continue
    if e['id'] in KEEP:
        continue
    url = ''
    for k in ('pia', 'tiget', 'eplus', 'rakuten', 'lawson', 'official'):
        if (e.get('links') or {}).get(k):
            url = e['links'][k]
            break
    if not url:
        for t in e.get('tickets') or []:
            if t.get('url'):
                url = t['url']
                break
    rows.append((e['id'], d, e.get('genre'), e.get('artist') or '', e.get('name') or '',
                 e.get('venue') or '', url))

ids = [str(r[0]) for r in rows]
io.open('tmp/del_ids_0922.txt', 'w', encoding='utf-8').write(','.join(ids))

md = io.open('tmp/del_list_0922.md', 'w', encoding='utf-8')
md.write('# 削除した公演（2026-09-22 朝）\n\n')
md.write('公演が終わったもの **%d件**。残したのは10件＝買える枠が生きている5件'
         '（id1904 配信〜10/4／id5587 9/25・9/26の舞台挨拶／id6253 視聴券〜9/25／id13482 11/7公演／id13937 アーカイブ〜9/27）＋別エージェントの独立チェックで見つかった5件（id77 MeseMoa. ツアー続行／id3757 配信の販売が9/30まで／id7009 10月公演あり／id13988 11/2に延期／id14033 10/27に日程変更）。\n\n' % len(rows))
md.write('| id | 公演日 | ジャンル | 公演名 | 会場 | 確認用URL |\n|---|---|---|---|---|---|\n')
for r in sorted(rows, key=lambda x: (x[1], x[0])):
    name = (r[4] or r[3]).replace('|', '｜')[:60]
    md.write('| %s | %s | %s | %s | %s | %s |\n'
             % (r[0], r[1], r[2], name, (r[5] or '').replace('|', '｜')[:24],
                ('[開く](%s)' % r[6]) if r[6] else '（URLなし）'))
md.close()
print('ids=%d  → tmp/del_ids_0922.txt / tmp/del_list_0922.md' % len(rows))
