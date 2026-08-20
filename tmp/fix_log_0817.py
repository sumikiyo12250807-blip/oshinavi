# -*- coding: utf-8 -*-
"""logs/assigned_2026-08-17.md を実物に合わせて追記する。
独立検証の指摘＝「保留9件」と書いたあとに5件が動いたのに記録が無い。
記録は後からユーザーが見る唯一の場所なので、実物と食い違わせない
（[[feedback_new_pool_ok_before_assign]] C＝後から見られるリンクを残す）。"""
import io, os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))}
pool = sorted(e['id'] for e in EV.values() if e.get('genre') == 'new')

L = ['', '---', '',
     '## 🔧 8/17 昼の便のあと（保留9件のその後・実物に合わせた追記）', '',
     '朝の便で「保留9件」と書いたが、そのあとユーザーの指示で5件が動いた。**新着タブに残っているのは4件**。', '']

L.append('### ユーザー指示で追加したジャンル2つ')
L.append('')
L.append('| 表示 | キー | 用途 |')
L.append('|---|---|---|')
L.append('| シャンソン | `chanson` | ぴあの「音楽/シャンソン」に対応先が無かったため新設 |')
L.append('| その他 | `musicetc` | ぴあが「音楽その他」としか言わず中身からも決められないものの受け皿（音楽グループの最後） |')
L.append('')
L.append('### 保留9件のうち5件が動いた')
L.append('')
L.append('| id | 公演名 | どうなったか | URL |')
L.append('|---|---|---|---|')
rows = [
    (4427, 'musicetc に振り分け（受け皿ジャンル新設により決着）'),
    (4456, 'musicetc に振り分け。⚠️あたし=jpop／エージェント=hiphop で判定が割れた件。'
           'ぴあ実ページの出演は「BARK」のみで裏が取れず、hiphop の根拠が確認できなかったため'
           '「決められない」を正直に出す musicetc にした'),
    (4485, 'musicetc に振り分け（ぴあ=音楽その他・低確信だったため）'),
    (4448, 'chanson に振り分け。ユーザー指示「まとめる」で 4476 を統合し枠2本を保持'),
    (4476, '4448 に統合して削除（欠番）。両方の販売枠は 4448 に残している'),
]
for eid, what in rows:
    e = EV.get(eid)
    url = ((e.get('links') or {}).get('pia') if e else 'https://t.pia.jp/pia/event/event.do?eventCd=2629201')
    name = e.get('artist', '') if e else '愛の讃歌 ミュゼットで散りばめる秋のシャンソンと映画音楽（4448へ統合）'
    L.append('| %d | %s | %s | %s |' % (eid, name.replace('|', '｜'), what, url))

L.append('')
L.append('### 🚨 途中でやらかして直したこと（記録として残す）')
L.append('- 4448 に 4476 を統合したとき枠2本を残したが、直後に `dedup_badges.py` を流したため'
         '**表示が完全一致する枠として畳まれ、まだぴあで販売中の eventCd=2629201 の売り場が消えた**。')
L.append('- push直前の独立検証で発覚 → `tmp/restore_4448_slot_0817.py` で復元済み（枠2本・売り場URL2本）。')
L.append('- ⚠️**未解決**＝2枠はバッジの文字が完全に同じ（ぴあに1部/2部の時刻が載っていない）。'
         'このままだと次に `dedup_badges` を流すとまた畳まれる。'
         '主催（アートポケットカンパニー 090-2559-5629）に1部2部を確認して券種名を分けるのが本筋。')
L.append('')
L.append('### いま新着タブに残っている %d件（判断待ち）' % len(pool))
L.append('')
L.append('| id | 公演名 | URL |')
L.append('|---|---|---|')
for eid in pool:
    if eid > 4400 and eid >= 4489:
        continue
    e = EV[eid]
    L.append('| %d | %s | %s |' % (eid, e.get('artist', '').replace('|', '｜'),
                                   (e.get('links') or {}).get('pia', '')))
L.append('')
L.append('※ 上記のほかに、今日投入した新着 id4489-4538（50件・全部これから発売）がプールに入っている。')

p = 'logs/assigned_2026-08-17.md'
old = io.open(p, encoding='utf-8').read()
io.open(p, 'w', encoding='utf-8').write(old.rstrip('\n') + '\n' + '\n'.join(L) + '\n')
print('追記しました → %s（%d行追加 / 現在プール %d件）' % (p, len(L), len(pool)))
