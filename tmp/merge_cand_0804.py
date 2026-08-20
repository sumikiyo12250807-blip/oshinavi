# -*- coding: utf-8 -*-
"""cand_0804.json の「同じ公演が複数候補に割れている」分を1エントリに統合する。
・シルク・ドゥ・ソレイユ クーザ 東京公演 2月/3月/4月 → 長期公演は1エントリ(feedback_longrun_event)
・わたしたちのルノワール 一般/ペア → 券種違いは1エントリ(feedback_tickets_all_expand)
・コンサドーレ札幌の同一カード(通常/割引/駐車券) → 1試合1エントリ
統合後に newid を振り直す（未投入なので採番自由）。
"""
import io
import json

MERGES = [
    ('シルク・ドゥ・ソレイユ アース製薬 クーザ 東京公演',
     ['シルク・ドゥ・ソレイユ アース製薬 クーザ 東京公演／2月',
      'シルク・ドゥ・ソレイユ アース製薬 クーザ 東京公演／3月',
      'シルク・ドゥ・ソレイユ アース製薬 クーザ 東京公演／4月']),
    ('わたしたちのルノワール 日本が愛した、幸せの画家',
     ['わたしたちのルノワール 日本が愛した、幸せの画家',
      'わたしたちのルノワール 日本が愛した、幸せの画家 ＜一般前売ペア＞']),
    ('北海道コンサドーレ札幌対大分トリニータ',
     ['北海道コンサドーレ札幌対大分トリニータ ■■■車いす・シニア・手帳割引・Ｕ－２３他',
      '北海道コンサドーレ札幌対大分トリニータ 明治安田Ｊ２リーグ',
      '北海道コンサドーレ札幌対大分トリニータ 明治安田Ｊ２リーグ 大和ハウス プレミストドーム 駐車券']),
    ('北海道コンサドーレ札幌対栃木シティ',
     ['北海道コンサドーレ札幌対栃木シティ ■■■車いす・シニア・手帳割引・Ｕ－２３他',
      '北海道コンサドーレ札幌対栃木シティ 明治安田Ｊ２リーグ']),
]

cands = json.load(io.open('tmp/cand_0804.json', encoding='utf-8'))
by = {c['artist']: c for c in cands}
missing = [s for _, srcs in MERGES for s in srcs if s not in by]
assert not missing, '候補に無い名前: %s' % missing

drop = set()
for newname, srcs in MERGES:
    urls = []
    for s in srcs:
        for u in by[s]['urls']:
            if u not in urls:
                urls.append(u)
    by[srcs[0]]['artist'] = newname
    by[srcs[0]]['urls'] = urls
    drop |= set(srcs[1:])

out = [c for c in cands if c['artist'] not in drop or c['artist'] in {n for n, _ in MERGES}]
out = [c for c in cands if c['artist'] not in drop]
base = cands[0]['newid']
for i, c in enumerate(out):
    c['newid'] = base + i

json.dump(out, io.open('tmp/cand_0804.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
lines = ['統合後 %d エントリ / URL計 %d本 / newid %d..%d'
         % (len(out), sum(len(c['urls']) for c in out), out[0]['newid'], out[-1]['newid'])]
for c in out:
    lines.append('  %d %s (%d本)' % (c['newid'], c['artist'], len(c['urls'])))
io.open('tmp/cand_0804.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('merged -> %d entries (was %d)' % (len(out), len(cands)))
