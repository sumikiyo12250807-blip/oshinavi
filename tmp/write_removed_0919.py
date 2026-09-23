# logs/removed_2026-09-19.md を機械で書く（URLは index.html から抜いた tmp/del_cands_0919.json のまま）
import json
d = json.load(open('tmp/del_cands_0919.json', encoding='utf-8'))
keep = {1632: '9/23 東京公演（LINE CUBE SHIBUYA）が残っている＝日付と枠を直す',
        11415: '見逃し配信（アーカイブ）が10/2まで買える',
        11425: '14日間アーカイブの配信券あり・今も買えるか未確認＝保留',
        3683: '映画は9/18公開で上映中＝ムビチケの扱いをユーザーに相談'}
L = ['# 2026-09-19 朝 削除（公演が終わったエントリ・70件）', '',
     '判定＝check_expired で「公演終了（9/18）・全販売終了」に出た74件のうち、下の4件を除いた70件。',
     '別エージェントに「削除は誤りという前提で」実ページを全件開かせて独立に確かめた（ぴあ42・e+1・TIGET43 URL、開けなかった0）。',
     '公演が9/18以前に全部終わったと実ページで確かめられた 70/74。', '',
     '## 残した4件', '']
for o in d:
    if o['id'] in keep:
        L += [f"- id{o['id']} {o['name']}＝{keep[o['id']]}", f"  - {o['url']}"]
L += ['', '## 消した70件', '']
for o in d:
    if o['id'] not in keep:
        L += [f"- id{o['id']} {o['name']} @ {o['venue']}（公演 {o['date']}）", f"  - {o['url']}"]
L += ['', '別件：id659 押尾コータロー 2026 は date が 9/18（愛知）のままで「終わった」扱いになっていた。',
      '実際は2027-04-25（石川）までツアーが続く＝消さずに date/dateLabel/venue を全国ツアーに直した。']
open('logs/removed_2026-09-19.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('ok', len(d))
