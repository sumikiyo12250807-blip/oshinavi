# -*- coding: utf-8 -*-
"""新着49件(genre:new)を下書き_genre採用で振り分け。_piaSub空のengeki誤フォールバック6件は補正。
下書きフィールド(_genre/_extraGenres/_piaSub)を除去し、NEW_ORDERを空にする。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

# _piaSub空でengeki等に誤フォールバックした分の補正（中身で判定）
OVERRIDE = {
    2777: 'yougaku',  # WORLD 25TH ANNIVERSARY DON DIABLO＝洋楽EDM DJ
    2780: 'fes',      # 白山アウトドアフェス＝屋外フェス
    2800: 'sports',   # MAZDA FAN FESTA at 富士スピードウェイ＝モータースポーツ
    2801: 'art',      # 北海道ペット&ファミリー EXPO＝イベント
    2799: 'art',      # マーキー FreeStyle カルチャー Talk＝音楽カルチャートーク(イベント枠)
    # 2784 ヴェッセル -宇宙の旅- は _genre=engeki(ぴあ 演劇/パフォーマンス)で正=据置
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

dist = {}
changed = 0
for e in E:
    if e.get('genre') != 'new':
        continue
    gid = e.get('id')
    g = OVERRIDE.get(gid, e.get('_genre') or 'jpop')
    e['genre'] = g
    exg = e.get('_extraGenres') or []
    if exg:
        e['extraGenres'] = exg
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    dist[g] = dist.get(g, 0) + 1
    changed += 1

bak = f'index.html.bak_0716_assign'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
# NEW_ORDER を空に
h2 = re.sub(r'const NEW_ORDER = \[[0-9,\s]*\]', 'const NEW_ORDER = []', h2)
open('index.html', 'w', encoding='utf-8').write(h2)

print(f'振り分け {changed}件 / backup {bak}')
print('分布:', json.dumps(dist, ensure_ascii=False))
