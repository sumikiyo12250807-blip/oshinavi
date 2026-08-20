# -*- coding: utf-8 -*-
"""キャッシュ済みの実ページ券種カードを【重複排除せず】数えて登録枠数と突合する。
reference_reconcile_pia_qc_gate の穴④(同じ締切日の別券種が枠数一致で隠れる)と、
突合スクリプト側のdedupで枠が潰れる型の両方を炙り出す。
"""
import re, io, json, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']
cache = json.load(io.open('tmp/indep_cache_0803.json', encoding='utf-8'))

BUY = ('受付中', '発売前', '販売期間中', '抽選受付', '先着')
DEAD = ('終了', '完売', '中止')
ng = 0
for e in new:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p:
        urls.append(p)
    for t in e.get('tickets') or []:
        if t.get('url') and t['url'] not in urls:
            urls.append(t['url'])
    raw, dead = [], []
    seen_url = set()
    for u in urls:
        for c in cache.get(u, []):
            k = json.dumps(c, ensure_ascii=False, sort_keys=True)
            if k in seen_url:      # 同じカードを別URLから二重に数えない
                continue
            seen_url.add(k)
            st = c.get('state') or ''
            if any(b in st for b in BUY):
                raw.append(c)
            elif any(d in st for d in DEAD):
                dead.append(c)
    reg = len(e.get('tickets') or [])
    if len(raw) != reg:
        ng += 1
        print('❌ id%d %s | 登録%d ⇄ 実カード%d' % (e['id'], e['name'][:30], reg, len(raw)))
        for c in raw:
            print('    [実] %s | %s | %s | %s %s' % (c.get('state'), (c.get('title') or '')[:44],
                                                    c.get('when'), c.get('pref'), c.get('perfdate')))
        for t in e.get('tickets') or []:
            print('    [登] %s' % (t.get('type') or '')[:66])
    if dead:
        print('ℹ️ id%d %s | 販売終了カード%d枚（載せないのが正）' % (e['id'], e['name'][:26], len(dead)))
print('\n=== 枠数不一致 %d / %d件 ===' % (ng, len(new)))
