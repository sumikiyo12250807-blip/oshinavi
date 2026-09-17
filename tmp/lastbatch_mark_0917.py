import json, io
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
for b in d['batches']:
    if b['date'] == '2026-09-16':
        b['assigned'] = True
        b['rechecked'] = True
        b['note'] += ' ／9/17朝に再チェック＝別エージェントがぴあ実ページ151枚からゼロで再導出（66件・一致64・ズレ2は登録の型どおり＝10804 DIAURA 締切時刻・10835 プリキュアの売り切れ回）。66件を振り分け（logs/assigned_2026-09-17.md）。'
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('ok')
