# -*- coding: utf-8 -*-
"""取りこぼし監査で出た新規5件は、**出演者名がエントリ名になっている**ので正式名に直す。
そのまま入れると「その人の単独公演」と誤読される（memory: feedback_no_fake_info）。

根拠＝別エージェントがぴあの実ページで確認した中身：
  6477 さだまさし   → すみだ五彩の芸術祭「みんなの佐渡裕デイ」（佐渡裕指揮・新日本フィル／
                      さだまさしはスペシャルゲスト。10/2は立川志の輔も）
  6478 さだまさし   → 水島裕プロデュースvol.10「笑う朗読3」
                      🚨さだまさしは**劇作・脚本**で出演しない＝名義のまま出したら嘘になる
  6481 清春         → New Acoustic Camp 2026（ELLEGARDEN・ストレイテナー・miwaほか総勢35組）
  6484 鈴木茂       → Tokyo Pop Chronicle（伊藤銀次・尾崎亜美・南佳孝・松本隆ほか）
  6486 SHOW-WA     → a-nation 2026（EXILE・浜崎あゆみ・超特急ほか）
"""
import json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NEW = {
    6477: ('すみだ五彩の芸術祭 みんなの佐渡裕デイ', 'fes'),
    6478: ('水島裕プロデュースvol.10 笑う朗読3', 'engeki'),
    6481: ('New Acoustic Camp 2026', 'fes'),
    6484: ('Tokyo Pop Chronicle', 'jpop'),
    6486: ('a-nation 2026', 'fes'),
}

d = json.load(open('tmp/leftover_built_0903.json', encoding='utf-8'))
out = []
for e in d:
    if e['id'] not in NEW:
        continue
    nm, g = NEW[e['id']]
    print('id%d 「%s」→「%s」 / _genre=%s' % (e['id'], (e.get('name') or '')[:26], nm, g))
    e['name'] = nm
    e['artist'] = nm
    e['_genre'] = g
    out.append(e)

json.dump(out, open('tmp/leftover_new_0903.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('→ tmp/leftover_new_0903.json（%d件）' % len(out))
