# -*- coding: utf-8 -*-
"""9/15夜のX主役選び（9/16発売）で、ユーザー「最近、xのフォロワー数で出してる？」を受けて測り足したフォロワー数を
tools/x_log.json の台帳（handle を持つ辞書のリスト）に足す／更新する。数はどれもブラウザ実測（x.com/<handle> の Followers）。
同じ handle があれば数とメモを上書き、無ければ末尾に足す。改行・インデントは元のファイルに合わせる（indent=1）。
使い方: python tmp/x0916/xlog_add_followers.py [--apply]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
NEW = [
    ('TOWA TEI', '@towatei', 53300, '2026-09-15 ブラウザ実測「53.3K」。本人'),
    ('WHITE JAM', '@WHITEJAM_STAFF', 33100, '2026-09-15 ブラウザ実測「33.1K」。表示名 WHITE JAM Official'),
    ('佐野元春', '@DaisyMusicInfo', 24600, '2026-09-15 ブラウザ実測「24.6K」。本人でなくレーベル DaisyMusic の公式（本人のXは無い）'),
    ('ミュージカル『ミス・サイゴン』', '@Miss_Saigon_JPN', 20600, '2026-09-15 ブラウザ実測「20.6K」。日本公演の公式'),
    ('chilldspot', '@chilldspot', 18100, '2026-09-15 ブラウザ実測「18.1K」。バンド公式'),
    ('三山ひろし', '@hiroshiouentai', 13200, '2026-09-15 ブラウザ実測「13.2K」。本人'),
    ('ワハハ本舗', '@wahahahompo', 7993, '2026-09-15 ブラウザ実測。劇団公式'),
    ('前川清', '@maekawa_kikaku', 5622, '2026-09-15 ブラウザ実測。事務所の公式'),
    ('神韻芸術団', '@ShenYunJA', 3832, '2026-09-15 ブラウザ実測。日本語版の公式'),
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
