# -*- coding: utf-8 -*-
"""組み上がりから抜き打ち検証の対象を選ぶ（状態が混ざるものを優先）。
一覧APIの言うことと実ページが合っているかを人が見て確かめるため。
"""
import io, json

built = json.load(open('tmp/built_fany_0921.json', encoding='utf-8'))


def kinds(e):
    k = set()
    for t in e['tickets']:
        if t.get('presaleEnded'):
            k.add('先行終了')
        elif t.get('saleEnded'):
            k.add('販売終了')
        elif t.get('startDate'):
            k.add('発売前/本日')
        else:
            k.add('販売中')
    return k


picks = []
want = [{'販売中', '先行終了'}, {'発売前/本日'}, {'販売中', '販売終了'}, {'販売中'}, {'発売前/本日', '先行終了'}]
for w in want:
    for e in built:
        if w <= kinds(e) and e not in picks:
            picks.append(e)
            break

out = io.open('tmp/fany_spotcheck.txt', 'w', encoding='utf-8')
for e in picks:
    out.write('=== id(仮) %s / %s\n' % (e['links']['fany'], e['name']))
    out.write('  出演: %s\n  会場: %s（%s）  公演: %s\n'
              % (e['artist'], e['venue'], e['prefecture'], e['dateLabel']))
    for t in e['tickets']:
        flags = ' '.join(k for k in ('soldout', 'saleEnded', 'presaleEnded', 'startDate')
                         if t.get(k))
        out.write('  - %s | date=%s | %s\n    %s\n' % (t['type'], t['date'], flags, t['url']))
    out.write('\n')
out.close()
print('wrote tmp/fany_spotcheck.txt  %d件' % len(picks))
for e in picks:
    print(e['links']['fany'])
