# -*- coding: utf-8 -*-
"""ヒール適用の前後で「画面に出る枠」が減ったエントリを数える。
出典 feedback_heal_flattens_ticket_types（阪神×広島 12枠→1枠を機械ゲートが全部素通りさせた）。

比較の相手は HEAD ではなく **ヒール直前のバックアップ** にする。
今朝は先に7件削除しているので HEAD と比べるとその分が差として出てしまう。
"""
import re, json, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-02'
BEFORE = 'index.html.bak_0902_noon_pre'   # heal --apply が取ったバックアップ


def load(path):
    h = open(path, encoding='utf-8').read()
    return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))


def base_type(ty):
    ty = re.sub(r'〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', ty or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$', '', ty)
    return ty.strip()


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)


def vis_keys(e):
    """画面に出る枠を「券種の基底名＋飛び先URL」で集める（日付の書き換えは同一視）"""
    return {(base_type(t.get('type')), (t.get('url') or '').strip())
            for t in (e.get('tickets') or []) if visible(t)}


old = {e['id']: e for e in load(BEFORE)}
new = {e['id']: e for e in load('index.html')}
print(f'エントリ数  ヒール前 {len(old)} → 後 {len(new)}')
gone = [i for i in old if i not in new]
if gone:
    print(f'🚨 エントリごと消えた: {gone}')

shrunk = []
for i, e in new.items():
    if i not in old:
        continue
    ko, kn = vis_keys(old[i]), vis_keys(e)
    lost = ko - kn
    if lost:
        shrunk.append((i, e.get('artist', ''), len(ko), len(kn), sorted(lost)))

print(f'画面に出る枠が減ったエントリ: {len(shrunk)}件')
for i, name, no, nn, lost in shrunk:
    print(f'  🚨 id={i} {name[:30]}  {no}枠 → {nn}枠')
    for k in lost[:12]:
        print(f'       - {k[0]}  {k[1]}')
tot_o = sum(len(vis_keys(e)) for e in old.values())
tot_n = sum(len(vis_keys(e)) for e in new.values())
print(f'画面に出る枠の総数: {tot_o} → {tot_n}  （差 {tot_n - tot_o:+d}）')
