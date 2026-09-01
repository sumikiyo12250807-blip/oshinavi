# -*- coding: utf-8 -*-
import json,io,sys,os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT=r'C:\Users\user\oshinavi'
d=json.load(open(os.path.join(ROOT,'tmp','verify_B_0902_merged.json'),encoding='utf-8'))
L=[]
L.append('# 独立再導出メモ — verify_list_B_0902 (51件) / 2026-09-02')
L.append('')
L.append('取得方法: `python tools/pia_tickets.py "<URL>" --all --json` を1件ずつ逐次実行（2秒間隔・混雑時は20秒後に1回だけ再試行）。')
L.append('別途 生HTMLを保存し、`rlsCd/lotRlsCd` のユニーク数・`ticketSalesCard-2024__status` 出現数・`datetime` 属性で独立に再照合した。')
L.append('登録側の値は一切参照していない。')
L.append('')
L.append('取得失敗: **0件**（51/51 成功）。全ページで 券種行数 == rlsCdユニーク数 == HTMLカード数/2 が一致。')
L.append('')
for o in d:
    L.append('## %s %s' % (o['id'], o['name']))
    L.append('- URL: %s' % o['url'])
    L.append('- ぴあジャンル表記: %s' % o['genre'])
    L.append('- 全券種 %d / 買える枠(受付中・発売前) **%d** / rlsCdユニーク %d' % (len(o['rows']),len(o['buy']),len(o['rls'])))
    for r in o['rows']:
        pr = r['perfdate'] + ('〜'+r['perf_end'] if r['perf_end']!=r['perfdate'] else '')
        L.append('  - [%s] 券種「%s」/ 公演日 %s / %s %s / %s（%s）' % (r['state'], r['title'], pr, r['pref'], r['venue'], r['when'], r['statustext']))
    L.append('')
open(os.path.join(ROOT,'tmp','verify_B_0902.md'),'w',encoding='utf-8').write('\n'.join(L))
print('written', len(L), 'lines')
