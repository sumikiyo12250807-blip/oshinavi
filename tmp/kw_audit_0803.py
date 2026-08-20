# -*- coding: utf-8 -*-
"""新着50件のうち【ツアー/巡回/シリーズの取りこぼしリスクが高い】アーティストだけ、
ぴあをキーワードで引き直して「登録に無いeventCd」を炙り出す。
memory: feedback_harvest_name_dedup_blindspot / feedback_tour_cross_channel_blindspot
        reference_pia_rate_limit_429（キーワード間を空ける）
"""
import re, io, json, sys, os, time, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

spec = importlib.util.spec_from_file_location('kw', os.path.join('tools', 'pia_kw_search.py'))
kw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kw)

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
CD = re.compile(r'event(?:Bundle)?Cd=(\w+)')
reg = set()
for e in EVENTS:
    p = (e.get('links') or {}).get('pia') or ''
    reg.update(CD.findall(p))
    for t in e.get('tickets') or []:
        reg.update(CD.findall(t.get('url') or ''))

KWS = ['プロレスリング・ノア', '中田カウス', '爆生', '立川寸志', '細田守', '竹久夢二',
       'ラフィンノーズ', '奥井亜紀', '白鳥英美子', '新浜レオン', '横山幸雄', '宮本笑里',
       'メジューエワ', '大須演芸場']

out = []
for k in KWS:
    try:
        rows = kw.search(k)
    except Exception as ex:
        out.append('❌ %s 取得失敗 %s' % (k, ex))
        continue
    rows = list(rows.values()) if isinstance(rows, dict) else rows
    miss = []
    for r in rows:
        cds = CD.findall(r.get('url') or '')
        if cds and not (set(cds) & reg):
            miss.append(r)
    out.append('\n■ %s : ぴあヒット%d件 / 未登録%d件' % (k, len(rows), len(miss)))
    for r in miss:
        out.append('   [%s%s] %s | %s | %s | %s' % (
            r.get('status'), (' ' + r['rlsdate']) if r.get('rlsdate') else '',
            (r.get('title') or '')[:44], r.get('perfdate'), r.get('venue'), r.get('url')))
    time.sleep(4)

io.open('tmp/kw_audit_0803.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
