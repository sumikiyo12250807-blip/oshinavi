# -*- coding: utf-8 -*-
"""新着プール34件のジャンル振り分け（2026-08-21 朝）。

原則＝**ぴあカテゴリで記憶した `_genre` をそのまま `genre` へ移す**（[[project_vendor_genre_autoassign]]）。
自分の音楽知識で再分類しない。手を入れるのは下の3件だけ：

  4739 おやじバンド合戦 松阪の陣
      _genre=fes だが会場は**クラギ文化ホール＝屋内**。
      保存ルールに「fesは複数組＋屋外／**屋内named-フェスはjpop**」と明記があるので **jpop**。
      （_piaSub が「音楽その他」＝名前fallback枠＝人が見る枠）

  4787 全日本ぎょうざ祭り2026秋
      _genre=kids だが、ぴあが**会場の業態**で「イベント/スクール・レジャー」を付けた型。
      中身は食のイベントなので **gourmet**（既存に2件あるジャンル）。
      ＝2026-08-01の「ぴあが業態でカテゴリを付けた時は主役で読み直す」補足の適用。

  4762 博品館劇場名作リーディングシアター
      _genre=engeki（ぴあ「朗読・リーディング」の確定マッピング）はそのまま主に据え、
      緒方恵美・鈴木達央・夏川椎菜ら**声優が主役の朗読劇**なので extraGenres に **seiyuu** を足す
      （ファンは声優名で探す＝[[feedback_oshikatsu_first]]／[[feedback_genre_both_when_unclear]]）。

あわせて 4770 の公演名を正式名称に直す（ぴあのイベント名が劇団名だけだった）。
  公式＝ https://www.onetwo-works.jp/ 「ワンツーワークス #44 シリーズ［時代を見つめる］② 『報道指針』」
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

OVERRIDE = {
    4739: ('jpop', [], '屋内ホールなので fes ではない（保存ルール＝屋内named-フェスはjpop）'),
    4787: ('gourmet', [], 'ぴあが会場業態でkidsを付けたが中身は食のイベント'),
    4762: ('engeki', ['seiyuu'], '声優が主役の朗読劇なので seiyuu をサブに追加'),
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
rows, n = [], 0
for e in EVENTS:
    if e['id'] == 4770:
        e['name'] = 'ワンツーワークス #44 シリーズ［時代を見つめる］② 『報道指針』'
        e['artist'] = '劇団ワンツーワークス'
        e['verifiedAt'] = '2026-08-21'
    if e.get('genre') != 'new':
        continue
    ov = OVERRIDE.get(e['id'])
    if ov:
        g, extra, why = ov
    else:
        g, extra, why = e.get('_genre'), list(e.get('_extraGenres') or []), 'ぴあカテゴリ（%s）のまま' % e.get('_piaSub')
    assert g, e['id']
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    url = (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or ''
    rows.append((e['id'], e.get('name'), g, extra, why, url))
    n += 1

print('振り分け %d件' % n)
shutil.copyfile('index.html', 'index.html.bak_0821_assign')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])

# ログを残す（新着タブが空になる代わりの「見る場所」）
L = ['# 2026-08-21 朝の便：新着プールの振り分け（%d件）' % n, '',
     'ぴあカテゴリで記憶した下書き（_genre）をそのまま適用するのが原則。',
     '別エージェント1本に「下書きを見せずゼロから」ジャンルを判定させ、割れた3件だけ保存ルールに当てて決めた。', '',
     '| id | 公演名 | ジャンル | サブ | 根拠 | 確認用URL |', '|---|---|---|---|---|---|']
for i, name, g, extra, why, url in rows:
    L.append('| %d | %s | %s | %s | %s | %s |' % (
        i, name, g, '/'.join(extra) or '–', why, ('[ぴあ](%s)' % url) if url else '–'))
io.open('logs/assigned_2026-08-21.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('logs/assigned_2026-08-21.md を書いた')
