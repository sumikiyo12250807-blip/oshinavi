# -*- coding: utf-8 -*-
"""9/14夜のX主役選びでブラウザ実測したフォロワー数を tools/x_log.json の台帳（handle を持つ辞書のリスト）に足す／更新する。
同じ handle があれば数とメモを上書き、無ければ末尾に足す。改行・インデントは元のファイルに合わせる（indent=1）。
使い方: python tmp/x0914/xlog_add_followers.py [--apply]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
NEW = [
    ('映画名探偵プリキュア', '@precure_movie', 206400, '2026-09-14 ブラウザ実測。映画『映画名探偵プリキュア!不思議な庭と2人の秘密』の公式'),
    ('高橋健介', '@kensuke_mr6', 159600, '2026-09-14 ブラウザ実測。俳優本人'),
    ('大河ドラマ「豊臣兄弟!」', '@nhk_toyotomi', 107600, '2026-09-14 ブラウザ実測。NHK大河の公式（江戸東京博物館の特別展は展示なので主役にしない）'),
    ('反田恭平', '@kyohei0901', 95200, '2026-09-14 ブラウザ実測。本人'),
    ('吉本新喜劇', '@shinkigeki1', 84700, '2026-09-14 ブラウザ実測（8/11は84.2K）'),
    ('ディズニー・オン・クラシック', '@onClassicDisney', 57200, '2026-09-14 ブラウザ実測。公演の公式'),
    ('三菱重工浦和レッズレディース', '@REDSLADIES', 34600, '2026-09-14 ブラウザ実測。クラブ公式'),
    ('浅井健一', '@SSRstaff', 21200, '2026-09-14 ブラウザ実測。本人でなくレーベル SexyStones Records のスタッフ。ファンクラブ公式 @AsaiKenichi_FC は12.8K'),
    ('syrup16g', '@syrup16g_staff', 15800, '2026-09-14 WebSearch（15.8K・2023年1月開設）。スタッフ公式'),
]


def find_list(o):
    if isinstance(o, list) and o and all(isinstance(x, dict) and 'handle' in x for x in o):
        return o
    if isinstance(o, dict):
        for v in o.values():
            r = find_list(v)
            if r is not None:
                return r
    if isinstance(o, list):
        for v in o:
            r = find_list(v)
            if r is not None:
                return r
    return None


raw = io.open('tools/x_log.json', encoding='utf-8').read()
data = json.loads(raw)
lst = find_list(data)
assert lst is not None, '台帳のリストが見つからない'
by = {x.get('handle'): x for x in lst}
for name, h, n, note in NEW:
    if h in by:
        print('更新 %s %s %s → %s' % (name, h, by[h].get('followers'), n))
        by[h]['followers'] = n
        by[h]['note'] = note
    else:
        print('追加 %s %s %s' % (name, h, n))
        lst.append({'name': name, 'handle': h, 'followers': n, 'note': note})
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in raw else '\n'
io.open('tools/x_log.json', 'w', encoding='utf-8', newline='').write(json.dumps(data, ensure_ascii=False, indent=1).replace('\n', nl) + nl)
print('書き込み完了')
