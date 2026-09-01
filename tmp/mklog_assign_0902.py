# -*- coding: utf-8 -*-
"""今朝振り分けた101件を logs/assigned_2026-09-02.md に残す。
新着タブから消える代わりの「後から見る場所」（feedback_new_pool_ok_before_assign）。
URLは index.html から機械抽出（手で書かない）。"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ids = [int(x) for x in open('tmp/pia_new_ids_0902.txt', encoding='utf-8').read().split('\n')[1].split(',')]
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}

L = ['# 2026-09-02 新着プールの振り分け（ぴあ101件）', '',
     '9/1 に投入したぴあの発売前103件。今朝の流れ＝', '',
     '1. `reconcile_pia.py --ids`（機械照合）＝**OK 103・MISSING/DROP/STALE/FETCH/QC 全0**',
     '   （照合できた枠 111/130・未照合19は「同じ締切の枠が複数で対を確定できない」分）',
     '2. **別エージェント2本に、登録値を見せずゼロから再導出**させた（52件＋51件・全件取得成功）',
     '3. 同じ演目が東京/大阪で2エントリに割れていた2組を統合（下記）→ 101件を振り分け', '',
     '**判定のしかた**＝取得時にぴあのカテゴリで記憶した下書き `_genre` をそのまま適用する',
     '（自分の知識で再分類しない＝project_vendor_genre_autoassign／feedback_genre_pia_asis_and_other）。', '',
     '## 統合した2組（ツアーは1エントリ＝feedback_tour_consolidate）', '',
     '- **id6136 舞台「呪術廻戦」-渋谷事変前編-** ← id6137（大阪）を畳んだ。4枠・11/14〜11/29',
     '- **id6105 劇団「ハイキュー!!」“勝者と敗者”** ← id6106（大阪）を畳んだ。4枠・12/19〜R9年1/11', '',
     '## 直したもの', '',
     '- **id6159 藝大定期邦楽 第92回** … ぴあ区分「クラシック/クラシック邦楽」＝演奏を聴く側なので',
     '  `dento`（舞台）→ **`hougaku`（音楽）**。9/1に伝統を2つに割ったとき',
     '  `build_pia_entries.py` の対応表を直し忘れていたので、**道具と回帰テストも直した**。', '',
     '| id | 公演名 | ジャンル | 公演日 | 確認用URL |', '|---|---|---|---|---|']

n = 0
for i in ids:
    e = by.get(i)
    if not e:
        L.append(f'| {i} | （統合で欠番） | – | – | – |')
        continue
    u = ((e.get('links') or {}).get('pia') or '')
    ex = e.get('extraGenres') or []
    g = (e.get('genre') or '') + ('＋' + '/'.join(ex) if ex else '')
    L.append(f"| {i} | {e.get('artist','')} | {g} | {e.get('date','')} | "
             f"{('[ぴあ](%s)' % u) if u else '–'} |")
    n += 1
L += ['', f'計 {n}件（＋統合で欠番 2件）', '',
      '## 振り分けていないもの', '',
      '- **e+ の162件はプールに残した**＝ぴあ以外は毎回ユーザーが目視で確認する決まり',
      '  （feedback_nonpia_user_eyes_until_gate）。OSHINAVI の新着タブで見てもらう。']
os.makedirs('logs', exist_ok=True)
open('logs/assigned_2026-09-02.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print(f'wrote logs/assigned_2026-09-02.md  {n}件')
