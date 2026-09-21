# -*- coding: utf-8 -*-
"""ZAIKOの一覧462件の傾向を見る＝公演日の分布・県・主催（サブドメイン）・日付が取れたか。
ビルダーを書く前に「何が入っている売り場か」を数字で押さえる。
"""
import collections, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(io.open('tmp/zaiko_0921.json', encoding='utf-8'))
rows = d['list']
out = io.open('tmp/x0921/zaiko_list_survey.txt', 'w', encoding='utf-8')
out.write('一覧 %d件（引いた時刻 %s）\n\n' % (len(rows), d.get('fetched_at')))

nodate = [r for r in rows if not r.get('date')]
out.write('公演日が取れなかった %d件\n' % len(nodate))
bym = collections.Counter(r['date'][:7] for r in rows if r.get('date'))
out.write('\n=== 公演月別 ===\n')
for k, n in sorted(bym.items()):
    out.write('  %s %4d件\n' % (k, n))

out.write('\n=== 県（一覧から取れた分）上位20 ===\n')
for k, n in collections.Counter(r.get('pref') or '（取れない）' for r in rows).most_common(20):
    out.write('  %-12s %4d件\n' % (k, n))

out.write('\n=== 主催（サブドメイン）上位25 ===\n')
sub = collections.Counter(
    (re.match(r'https://([a-z0-9-]+)\.zaiko\.io', r['url']) or [None, '?'])[1] for r in rows)
for k, n in sub.most_common(25):
    out.write('  %-30s %4d件\n' % (k, n))

out.write('\n=== カテゴリ別 ===\n')
for k, n in collections.Counter(r['cat'] for r in rows).most_common():
    out.write('  %-28s %4d件\n' % (k, n))

out.write('\n=== 会場が取れなかった ===\n')
noven = [r for r in rows if not r.get('venue')]
out.write('  %d件\n' % len(noven))
for r in noven[:8]:
    out.write('    %s | %s\n' % (r['title'][:40], r['url']))

out.write('\n=== 先頭15件 ===\n')
for r in rows[:15]:
    out.write('  %s %s | %-34s | %s（%s）\n'
              % (r.get('date'), r.get('time') or '', r['title'][:34],
                 (r.get('venue') or '')[:20], r.get('pref') or ''))
out.close()
print('wrote tmp/x0921/zaiko_list_survey.txt')
