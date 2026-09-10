# -*- coding: utf-8 -*-
"""project_big_artist_crosscheck に「載っているが枠が足りない」層を書き足す。"""
import io

p = ('C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
     'project_big_artist_crosscheck.md')
s = io.open(p, encoding='utf-8').read()

anchor = '## 実測（2026-09-10・2週ぶん）'

add = '''## 🚨🚨 もう一段ある＝「載っているが**その週に発売が始まる枠が無い**」

名前が当たっても終わりではない。2026-09-10 に見つけた層＝
**エントリは載っている。でも持っている枠が「先行」だけで、一般発売の枠を1つも持っていない。**

| id | 組 | 持っていた枠 |
|---|---|---|
| 3568 | GENERATIONS from EXILE TRIBE | プレリザーブ6次（終了）／プリセール静岡だけ |
| 2990 | 森高千里 | 29枠あるのに全部プレリザーブ・先行 |
| 1308 | 清水ミチコ | 24枠あるのに全部プレリザーブ |
| 3422 | モーニング娘。'26 | 同上 |
| 4490 | アンジュルム | 同上 |

### なぜどのゲートも気づかないか

- `check_zero_badge.js` … **枠が1つでも生きていれば通る**（先行が生きているので出ない）
- 名前の突き合わせ … **名前があれば「載っている」で終わる**
- `reconcile_pia --new` … 新着プールしか見ない
- ヒール … `startDate == today` 型が対象

＝**この層はどのゲートも見ていなかった。**

### 道具（2026-09-10 追加）

```
python tools/check_big_artists.py <json> --window 2026-09-14:2026-09-20
```
`--window` を付けると「その窓に **startDate を持つ枠**があるか」まで見て、
無ければ **⚠️「載っているが、この窓に発売が始まる枠が無い」** で出す。
2週ぶんの実測＝**それぞれ8件ずつ**出た（合計16件・GENERATIONS／モーニング娘。'26／
アンジュルム／ウルフルズ／森高千里／清水ミチコ／松平健など）。

⚠️「潤」のような**短い名前は部分一致で誤爆する**。出たものは1件ずつ中身を見てから拾う。

'''

assert anchor in s and '枠が足りない' not in s
io.open(p, 'w', encoding='utf-8').write(s.replace(anchor, add + anchor, 1))
print('project_big_artist_crosscheck.md に「枠が足りない層」を追記')
