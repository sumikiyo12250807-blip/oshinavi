# -*- coding: utf-8 -*-
"""今夜のX投稿に出した公演の「取りこぼし」を、名前でぴあを引いて探す。

夜の便の手順8（day skill）＝**投稿の着地先に公演や枠が欠けていたら、
わざわざ来た人が自分の推しを見つけられない**＝いちばん損なパターン。
🚨ツアーまとめページ（bundle）だけ見ない＝アーティスト名で引き直す
（feedback_pia_bundle_hides_shows）。

出力は tmp/x_leftover_0902.txt（コンソールに日本語を出さない）。
"""
import os, re, sys, time
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import pia_kw_search as pks
from pia_missing_audit import load_events, registered_cds, load_excluded

MAT = 'tmp/x_material_0902.txt'
OUT = 'tmp/x_leftover_0902.txt'
WAIT = 5

names, cur = [], False
for ln in open(MAT, encoding='utf-8'):
    m = re.match(r'# (.+) に発売開始', ln)
    if m:
        cur = m.group(1).startswith('明日')
        continue
    m = re.match(r'^\s{2}\d{1,2}:\d{2}\s(.+?)／', ln)
    if m and cur:
        n = m.group(1).strip()
        if n not in names:
            names.append(n)
print('keywords =', len(names))

evs = load_events()
reg = registered_cds(evs)
excl = load_excluded()
pks.FILTERS = ['', 'rlsStatus=0102']      # 無フィルタ＋発売前（429を避けて2本だけ）

lines = ['# 今夜のX投稿に出した公演の取りこぼし監査（2026-09-02）', '',
         f'対象キーワード {len(names)}件／登録済みコード {len(reg)}件', '']
miss_total = 0
for i, kw in enumerate(names, 1):
    try:
        hits = pks.search(kw)
    except Exception as ex:
        lines.append(f'[{i}/{len(names)}] {kw} … 取得失敗 {str(ex)[:40]}')
        time.sleep(WAIT)
        continue
    miss = []
    for h in hits.values():          # search() は url -> item の dict を返す
        u = h.get('url') or ''
        m = re.search(r'event(?:Bundle)?Cd=(b?\d+)', u)
        cd = m.group(1) if m else ''
        if cd and cd not in reg and cd not in excl:
            miss.append(h)
    if miss:
        miss_total += len(miss)
        lines.append(f'[{i}/{len(names)}] 🚨 {kw} … 未登録 {len(miss)}件')
        for h in miss:
            lines.append(f"      {h.get('title','')[:52]} | 公演{h.get('perfdate','')} | "
                         f"発売{h.get('rlsdate','')} | {h.get('venue','')[:32]}")
            lines.append(f"      {h.get('url','')}")
    else:
        lines.append(f'[{i}/{len(names)}] ok {kw} … 取りこぼしなし（ヒット{len(hits)}）')
    time.sleep(WAIT)
lines += ['', f'=== 未登録の候補 合計 {miss_total}件 ===']
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('wrote', OUT, 'missing=', miss_total)
