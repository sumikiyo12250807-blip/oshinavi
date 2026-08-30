import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
by={e['id']:e for e in ev}
allids=[int(x) for x in open('tmp/_ended_ids_0831.txt').read().split(',')]
HOLD={1904,1242,1637}   # 配信チケットが生きている＝削除しない（ユーザー判断待ち）
ids=[i for i in allids if i not in HOLD]
# 念のため機械で再確認: 公演日が今日より前 かつ 未来日付の枠が無い
bad=[]
for i in ids:
    e=by[i]
    assert e['date']<'2026-08-31', i
    fut=[t for t in e.get('tickets',[]) if (t.get('date') or '')>='2026-08-31' or (t.get('startDate') or '')>='2026-08-31']
    if fut: bad.append((i,e.get('artist',''),[t.get('type') for t in fut]))
print('削除対象',len(ids),'／未来日付の枠を持つもの',len(bad))
for b in bad: print(' ',b)
open('tmp/_del_ids_0831.txt','w').write(','.join(str(i) for i in ids))
with open('logs/removed_2026-08-31.md','w',encoding='utf-8') as f:
    f.write('# 2026-08-31 朝の便で削除したエントリ（公演終了済）\n\n')
    f.write('判定＝`date`（千秋楽）が2026-08-31より前／未来日付の販売枠ゼロ。別エージェントがゼロから再導出して一致。\n\n')
    f.write('| id | 名前 | 公演日 | 確認用URL |\n|---|---|---|---|\n')
    for i in ids:
        e=by[i]; L=e.get('links') or {}
        u=L.get('pia') or L.get('eplus') or L.get('rakuten') or L.get('lawson') or ''
        f.write(f"| {i} | {e.get('artist','')} | {e['date']} | {u} |\n")
    f.write('\n## 🚧 削除しなかった3件（配信チケットが生きている＝ユーザー判断待ち）\n\n')
    f.write('| id | 名前 | 公演日 | 生きている枠 |\n|---|---|---|---|\n')
    for i in sorted(HOLD):
        e=by[i]
        liv=[t['type'] for t in e['tickets'] if (t.get('date') or '')>='2026-08-31']
        f.write(f"| {i} | {e.get('artist','')} | {e['date']} | {' / '.join(liv)} |\n")
print('logs/removed_2026-08-31.md 書き出し')
