# -*- coding: utf-8 -*-
"""新着プール134件のジャンル振り分け（2026-08-21・今日投入した147件から統合分を引いた数）。

原則＝**ぴあカテゴリで記憶した `_genre` をそのまま `genre` へ**（[[project_vendor_genre_autoassign]]）。
🚨検証エージェント3本は「rock/idol に細分」する案を出してきたが、これは保存ルールに反するので採らない
   （ぴあが pop/rock/idol/folk/メタルを「音楽/J-POP・ROCK」1つにまとめている以上、人が細分しない。
    2026-06-23 にマカロニえんぴつで是正された件）。**あたしがエージェントにこのルールを伝え忘れたのが原因**。

手を入れるのは下の3種だけ:
 A ぴあが「会場の業態/大分類」でカテゴリを付けた時に**主役で読み直す**もの
 B **fes の判定**（複数組＋屋外の時だけ fes）＝ぴあカテゴリでは分からない軸
 C **サブジャンルの追加**（[[feedback_genre_both_when_unclear]]＝迷ったら両方）。
   ただし rock/idol など「ぴあが分けていない音楽ジャンルの細分」はサブにも入れない。
 ＋ユーザーが直接決めた4件（2026-08-21）。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

# (主ジャンル, サブ, 理由)  主が None なら _genre のまま
OVERRIDE = {
    # --- ユーザーが直接決めた4件（2026-08-21）---
    4799: ('classic', ['jazz'], 'ユーザー判断「両方」＝アルゼンチンタンゴの11人編成'),
    4812: ('classic', [], 'ユーザー判断「クラシック」＝ヴァイオリン×ピアノのデュオ'),
    4863: ('engeki', ['musical'], 'ユーザー判断「両方」＝1幕が会話劇・2幕がショートライブ'),
    4930: ('sports', [], 'ユーザー判断「スポーツ」＝ボディビル/フィットネスの大会'),
    # --- A ぴあが大分類でまとめた時に主役で読み直す ---
    4810: ('kpop', [], 'ぴあは「海外ROCK・POPS」だが韓国5人組ガールズグループ。既存kpop8件も全部韓国勢'),
    # --- B fes（複数組＋屋外）---
    4873: ('fes', [], '安平町ときわ公園＝屋外・STU48ほか40組超の2日間'),
    4881: ('fes', [], '万博記念公園もみじ川芝生広場＝屋外・阿部真央/高橋優/GLIM SPANKYら複数組'),
    # --- C サブジャンルの追加（両方持ち）---
    4811: (None, ['classic'], '昭和歌謡が演目・演者は音大出の声楽家＋ピアノ/ヴァイオリン'),
    4855: (None, ['dento'], 'メンデルスゾーンをオケで演奏＋狂言師 野村萬斎の語り'),
    4877: (None, ['anime'], 'アニソン/ゲーソン歌手のツアー'),
    4878: (None, ['anime'], '同上'),
    4899: (None, ['musical'], '着ぐるみマスクプレイの子ども向けミュージカル'),
    4926: (None, ['anime', 'kids'], 'プリキュア主題歌をオーケストラで演奏・お子さまのクラシックデビュー企画'),
    4920: (None, ['classic'], '箏＝邦楽だが新曲リサイタル'),
    4837: (None, ['engeki'], '宝塚に着想した劇団のミュージカル仕立ての芝居＋レビュー'),
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
rows, n = [], 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g, extra, why = e.get('_genre'), list(e.get('_extraGenres') or []), 'ぴあカテゴリ（%s）のまま' % (e.get('_piaSub') or '名前fallback')
    ov = OVERRIDE.get(e['id'])
    if ov:
        og, oex, owhy = ov
        if og:
            g = og
        for x in oex:
            if x not in extra:
                extra.append(x)
        why = owhy
    assert g, e['id']
    e['genre'] = g
    if extra:
        e['extraGenres'] = [x for x in extra if x != g]
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    url = (e.get('links') or {}).get('pia') or ''
    rows.append((e['id'], e.get('name'), g, e.get('extraGenres') or [], why, url))
    n += 1

print('振り分け %d件' % n)
shutil.copyfile('index.html', 'index.html.bak_0821_assign2')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])

L = ['# 2026-08-21 午前の便：新着プールの振り分け（%d件）' % n, '',
     '今日投入した147件から、統合・二重登録の整理で13件を畳んだ残り。',
     'ぴあカテゴリで記憶した下書き（_genre）をそのまま適用するのが原則。',
     '別エージェント3本（50/50/47件）に下書きを見せずゼロから判定させ、**保存ルールに照らして採否を決めた**。',
     '',
     '🚨エージェントは rock/idol への細分を提案してきたが採らなかった＝ぴあが「音楽/J-POP・ROCK」に',
     'まとめている以上、人が細分しないのが保存ルール（2026-06-23 マカロニえんぴつの是正）。',
     'あたしがエージェントへの指示にこのルールを書き忘れたのが原因。', '',
     '| id | 公演名 | ジャンル | サブ | 根拠 | 確認用URL |', '|---|---|---|---|---|---|']
for i, name, g, extra, why, url in rows:
    L.append('| %d | %s | %s | %s | %s | %s |' % (
        i, name, g, '/'.join(extra) or '–', why, ('[ぴあ](%s)' % url) if url else '–'))
io.open('logs/assigned_2026-08-21_am.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('logs/assigned_2026-08-21_am.md を書いた')
