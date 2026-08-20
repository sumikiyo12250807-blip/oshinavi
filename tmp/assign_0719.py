# -*- coding: utf-8 -*-
"""新着47件(2865-2914)のジャンル振り分け。
_piaSub由来の下書きをそのまま採用し、誤フォールバック分だけ実態に補正（全件裏取り済）。
"""
import re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
BAK = 'index.html.bak_0719_assign'
shutil.copy(PATH, BAK)
h = open(PATH, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

# 下書き(_genre)から変更する分だけ明示（理由＝実ページ/公式で裏取り済み）
OVERRIDE = {
    2873: ('idol', None),        # ハロ!コン＝モー娘。/アンジュルム等ハロプロ全グループ
    2877: ('fes', None),         # 複数組＋屋外(キトウシ森林公園)＝fesの定義に合致
    2871: ('kids', ['classic']), # 絵本朗読＋ヴァイオリン/ピアノ生演奏・2歳以上有料のファミリー向け
    2883: ('seiyuu', None),      # 山寺宏一/大塚明夫ほか声優13名の口演ライブ
    2913: ('hiphop', ['sports']),# ダンスバトル大会(8回目・コンペ形式)＝迷うので両方式
    2914: ('kids', None),        # 0歳から入場可・3歳以上有料の子ども向け音楽イベント
    # ぴあの「音楽/J-POP・ROCK」はjpopとrockを区別しないカテゴリ＝ロックバンドは実態へ
    2866: ('rock', None),        # The BONEZ／SHADOWS
    2867: ('rock', None),        # 中島卓偉
    2869: ('rock', None),        # Hakubi
    2872: ('rock', None),        # キノコホテル
    2876: ('rock', None),        # LEGO BIG MORL
}

from collections import Counter
cnt = Counter()
for e in E:
    if e.get('genre') != 'new':
        continue
    i = e['id']
    if i in OVERRIDE:
        g, extra = OVERRIDE[i]
        if extra:
            e['extraGenres'] = extra
    else:
        g = e.get('_genre')
    if not g:
        print(f'[!] id={i} ジャンル未決 {e.get("name")}')
        continue
    e['genre'] = g
    cnt[g] += 1
    e.pop('_genre', None)
    e.pop('_piaSub', None)
    e.pop('_srcgenre', None)

new_arr = json.dumps(E, ensure_ascii=False, indent=2)
new_arr = '\n'.join(('  ' + ln if ln.strip() else ln) for ln in new_arr.split('\n')).lstrip()
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER はそのまま（新着タブの並び順を投入順で固定）
open(PATH, 'w', encoding='utf-8').write(h)
print('振り分け:', dict(cnt), '計', sum(cnt.values()))
print('genre:new 残', sum(1 for e in E if e.get('genre') == 'new'))
print('_genre 残', sum(1 for e in E if '_genre' in e))
print(f'(backup {BAK})')
