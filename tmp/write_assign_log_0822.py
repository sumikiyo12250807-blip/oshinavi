# -*- coding: utf-8 -*-
"""2026-08-22 の振り分け結果を logs/assigned_2026-08-22.md に残す。

[[feedback_new_pool_ok_before_assign]]＝振り分けは自走してよいが、
**公演名＋割り当てジャンル＋確認用URL**を後から見られる形で残すこと（新着タブが空になる代わりの見る場所）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
E = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}
rows = [l.rstrip('\n') for l in io.open('tmp/assign_result_0822.txt', encoding='utf-8')][2:]

HOLD_WHY = {
    4950: 'ぴあは「海外ROCK・POPS」＝表どおりなら yougaku。でも OSHINAVI は韓国勢を kpop で運用中（Stray Kids 等8件）',
    4979: 'ぴあは「映画/邦画」＝前例なら engeki。でも中身はシネマ歌舞伎＝歌舞伎ルールなら dento',
    5002: 'ぴあは「スクール・レジャー」＝対応表では kids。でも中身は酒蔵めぐり＝前例（4260 サケマルシェ）なら gourmet',
    5005: 'ぴあは「祭り・花火大会」で名前に花火なし＝自動だと fes。でも OSHINAVI の fes 定義は「複数組＋屋外」',
    5010: 'ぴあが「イベントその他」＝決め手なし。engeki（その他の前例）か sports かで割れる',
    5011: 'ぴあは「学園祭」＝会場の業態カテゴリ。前例なら engeki だが、主役ルールで見ると seiyuu',
    5014: 'ぴあは「ショー・ファンイベント」＝対応表が意図的に未収載（主役で決める枠）。RAY YUZUKA が誰かの裏取りが要る',
    5018: '4950 と同じ＝ぴあは海外ROCK・POPS だが ONEW は韓国勢。yougaku / kpop で割れる',
    5035: '5002 と同じ＝ぴあはスクール・レジャーだが中身はワイン。kids / gourmet で割れる',
    5038: 'ぴあが「イベントその他」＝決め手なし。作家として見るか元アイドルとして見るかで engeki / jpop が割れる',
}

L = [
    '# 2026-08-22 新着プールの振り分け（77件）',
    '',
    '前夜（8/21）に投入した87件＋今日その場で作ったウルフルズ（5043）。',
    '',
    '**判定のしかた**＝ぴあのカテゴリで取得時に記憶した下書き `_genre` をそのまま適用する',
    '（project_vendor_genre_autoassign＝自分の音楽知識で再分類しない・J-POP・ROCK は jpop 固定）。',
    '別エージェントに下書きを見せずゼロから判定させ、**87件中74件が一致**。割れた2件はエージェント側を採用した。',
    '',
    '| id | 公演名 | ジャンル | 確認用URL |',
    '|---|---|---|---|',
]
n = 0
for r in rows:
    if not r.strip() or r.startswith('振り分け'):
        continue
    parts = [x.strip() for x in r.split('|')]
    if len(parts) < 4:
        continue
    i, name, g, url = parts[0], parts[1], parts[2], parts[3]
    if g.startswith('HOLD'):
        continue
    n += 1
    ex = E[int(i)].get('extraGenres') or []
    L.append('| %s | %s | %s%s | %s |' % (
        i, name, g, ('＋' + '/'.join(ex)) if ex else '', ('[ぴあ](%s)' % url) if url else '–'))

L += [
    '',
    '計 %d件' % n,
    '',
    '## 🚨 ぴあの実カテゴリで下書きを上書きした2件（エージェントの手柄）',
    '',
    'どちらも `_piaSub` が空で、うちの下書きが**名前からの推測（engeki）**になっていた。',
    'エージェントがぴあの詳細検索（sg フィルタ）で実カテゴリを突き止めてくれた。',
    '',
    '- **4960 森山直太朗** … engeki → **jpop**（ぴあ 音楽/J-POP・ROCK）',
    '- **5016 TJHiroshima チケット企画** … engeki → **sports**（ぴあ スポーツ/ゴルフ）',
    '',
    '## 副ジャンルを足した1件',
    '',
    '- **5021 花澤香菜** … jpop ＋ **seiyuu**（既存の前例 4242 神谷浩史・3582 水瀬いのり に揃えた）',
    '',
    '## ⚠️ 振り分けずプールに残した10件（相談）',
    '',
    '| id | 公演名 | 迷いどころ | 確認用URL |',
    '|---|---|---|---|',
]
for i in sorted(HOLD_WHY):
    e = E[i]
    L.append('| %s | %s | %s | [ぴあ](%s) |' % (i, e['name'], HOLD_WHY[i], (e.get('links') or {}).get('pia', '')))

L += [
    '',
    '## 📌 添えておく（決めたけど気になる分）',
    '',
    '- **4972〜4977 からぴちパラダイス LV ／ 4990 プロセカ LV** … ぴあのカテゴリ「映画/ライブビューイング」どおり engeki にした。',
    '  ただし `build_pia_entries.py` の対応表に「**中継元が音楽なら要手直し**」というコメントがあり、この8件は中継元が音楽ライブ。',
    '  直すなら次の機会に（宝塚 4981 は前例どおり engeki でよい）。',
    '- **4999 寺尾聰** … dinnershow で確定。アーティスト側のジャンルはぴあに分類が無く裏取りできなかったので付けていない。',
    '',
    '## 🧹 積み残し',
    '',
    '- 振り分け済みなのに `_genre` の下書きが残っているエントリが **66件**ある（今日より前からの積み残し・表示には影響しない）。',
    '  掃除は次の機会に。',
]
io.open('logs/assigned_2026-08-22.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('logs/assigned_2026-08-22.md を書いた（振り分け %d件 / 相談 %d件）' % (n, len(HOLD_WHY)))
