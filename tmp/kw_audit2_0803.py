# -*- coding: utf-8 -*-
"""新着50件の【残り全部】をぴあでキーワード再検索し、未登録eventCdを炙り出す（第2弾）。
第1弾(tmp/kw_audit_0803.py)で引いた14語は除く。
"""
import re, io, json, sys, os, time, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join('tools', fname))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

kw = load('kw', 'pia_kw_search.py')
pma = load('pma', 'pia_missing_audit.py')

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
CD = re.compile(r'event(?:Bundle)?Cd=(\w+)')
reg = set()
for e in EVENTS:
    reg.update(CD.findall((e.get('links') or {}).get('pia') or ''))
    for t in e.get('tickets') or []:
        reg.update(CD.findall(t.get('url') or ''))
excl = pma.load_excluded()

DONE = ['プロレスリング・ノア', '中田カウス', '爆生', '立川寸志', '細田守', '竹久夢二',
        'ラフィンノーズ', '奥井亜紀', '白鳥英美子', '新浜レオン', '横山幸雄', '宮本笑里',
        'メジューエワ', '大須演芸場']
# 語が広すぎて数百件返るものは監査対象外（別の切り口で見る）
TOOWIDE = ['宝塚歌劇', '仮面ライダー']

new = [e for e in EVENTS if e.get('genre') == 'new']
kws = []
for e in new:
    a = (e.get('artist') or e.get('name') or '').strip()
    a = re.split(r'[／/]', a)[0]
    a = re.sub(r'[（(].*?[)）]', '', a).strip()
    if len(a) < 3:
        a = (e.get('artist') or e.get('name') or '').strip()
    if any(d in a for d in DONE) or any(t in a for t in TOOWIDE):
        continue
    if a not in kws:
        kws.append(a)

print('引くキーワード %d語' % len(kws))
out = ['=== 新着50件の取りこぼし監査・第2弾 (%d語) ===' % len(kws)]
tot = 0
for i, k in enumerate(kws):
    try:
        found = kw.search(k)
    except Exception as ex:
        out.append('\n■ %s : 取得失敗 %s' % (k, ex))
        continue
    miss = []
    for u, x in found.items():
        c = CD.findall(u)
        if not c or c[0] in reg or c[0] in excl:
            continue
        miss.append((pma.same_name(k, x['title']), x, u))
    own = [m for m in miss if m[0]]
    oth = [m for m in miss if not m[0]]
    tot += len(own)
    out.append('\n■ %s : ヒット%d / 未登録%d（本人名義%d）' % (k, len(found), len(miss), len(own)))
    for flag, x, u in own + oth:
        out.append('   %s[%s%s] %s | %s | %s | %s' % (
            '' if flag else '(別名義)', x['status'], (' ' + x['rlsdate']) if x['rlsdate'] else '',
            x['title'][:40], x['perfdate'], x['venue'], u))
    print('[%d/%d] %s hits=%d missing=%d own=%d' % (i + 1, len(kws), k, len(found), len(miss), len(own)))
    time.sleep(3)

out.append('\n=== 本人名義の未登録 合計 %d件 ===' % tot)
io.open('tmp/kw_audit2_0803.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('→ tmp/kw_audit2_0803.txt  本人名義の未登録合計 %d' % tot)
