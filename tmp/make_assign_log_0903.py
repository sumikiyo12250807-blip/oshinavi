# -*- coding: utf-8 -*-
"""9/3 に振り分けた87件の一覧を logs/assigned_2026-09-03.md に残す。
公演名＋割り当てジャンル＋確認用URL（memory: feedback_new_pool_ok_before_assign のC「残す」）。
URLは index.html から機械抽出のみ（手で書かない）。
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

IDS = json.load(open('tmp/newpool_to_assign_0903.json'))
src = open('index.html', encoding='utf-8', newline='').read()
events = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
byid = {e['id']: e for e in events}


def url_of(e):
    cands = []
    L = e.get('links')
    if isinstance(L, dict):
        cands = [v for v in L.values() if isinstance(v, str) and v.startswith('http')]
    elif isinstance(L, list):
        for x in L:
            if isinstance(x, dict):
                cands += [v for v in x.values() if isinstance(v, str) and v.startswith('http')]
    for t in e.get('tickets', []):
        u = t.get('url')
        if isinstance(u, str) and u.startswith('http'):
            cands.append(u)
    return cands[0] if cands else '(URL無し)'


rows = []
for i in sorted(IDS):
    e = byid.get(i)
    if not e:
        continue
    g = e.get('genre')
    extra = e.get('extraGenres') or []
    gl = g + ('+' + '+'.join(extra) if extra else '')
    rows.append('| %d | %s | `%s` | %s |' % (i, (e.get('name') or '').replace('|', '/'), gl, url_of(e)))

head = """# 2026-09-03 振り分けた新着（87件）

ぴあ由来87件を振り分け。**e+由来の10件は保留**（下記）。

## 検証（自走の条件・memory feedback_new_pool_ok_before_assign）
- `reconcile_pia.py --new`＝OK86／MISSING 0／DROP 0／STALE 1／FETCH 0／QC 0、
  QC照合カバレッジ **110枠/113枠**（未照合3枠＝同締切で対を確定できない分）
- **別エージェント2本**に87件をゼロから再導出させた（登録値を見せずに実ページから）。
  ページ消失0・混雑0。枠数の食い違いは**ぴあの売り場コード(rlsCd/lotRlsCd)のユニーク数を自分で数え直して**決着
  （昼夜2回公演でもぴあ側は1枠で売っている＝登録が正しい）。
- ジャンルはエージェントに**ぴあのページ表記だけ**を写させて突合。

## 直したもの
- **id6297 ROCKY**＝ぴあ区分は「音楽/海外ROCK・POPS」だが、**元ASTROのラキ＝韓国のアーティスト**なので
  `kpop` に読み替え（memory feedback_kpop_vs_yougaku＝読み替えるのはこの区分のときだけ）。
  裏取り https://k-plaza.com/2026/08/rocky-260820.html
- **id6364 俺たちの旅**＝東京10/29枠が**予定枚数終了**だったので `soldout` を付けた（消さずに表示を継続）。

## ⚠️相談（振り分けずプールに残した10件＝全部e+由来）
6012, 6041, 6211, 6212, 6216, 6224, 6227, 6228, 6241, 6253
大半が「大学の学園祭のゲストらしいが、出演確定の告知が見つからない」もの。推測で振り分けない。

## 一覧

| id | 公演名 | ジャンル | 確認用URL |
|---|---|---|---|
"""
open('logs/assigned_2026-09-03.md', 'w', encoding='utf-8').write(head + '\n'.join(rows) + '\n')
print('logs/assigned_2026-09-03.md に %d件' % len(rows))
