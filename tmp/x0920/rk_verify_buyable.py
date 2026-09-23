# -*- coding: utf-8 -*-
"""組み上がった楽天11件が**本当に買えるか**を、AJAX（公演ごとの売り状態）で独立に確かめる。

🚨生HTMLの「購入する」の有無は当てにならない＝楽天の売り状態はAJAXにしか出ない
   （[[feedback_no_fake_info]]／tools/rakuten_perf_status.py の冒頭）。
出力: tmp/x0920/rk_buyable.md
"""
import importlib.util, io, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

spec = importlib.util.spec_from_file_location('ps', 'tools/rakuten_perf_status.py')
PS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PS)

t = io.open('tmp/x0920/rk_built2.txt', encoding='utf-8', errors='replace').read()
built = json.loads(t[t.find('['):])
urls = []
for e in built:
    u = (e.get('links') or {}).get('rakuten') or ''
    # deeplink から素のURLを戻す
    import urllib.parse
    q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
    urls.append(((e.get('artist') or '')[:52], q.get('murl', [u])[0]))

out = ['# 楽天11件＝AJAXで「本当に買えるか」を独立に確かめた（2026-09-20）\n',
       '生HTMLの「購入する」は当てにならない（後からAJAXで差し込まれる）ので、公演ごとの売り状態を直接聞いた。\n']
for name, u in urls:
    r = PS.perf_status(u)
    if not r.get('ok'):
        out.append('\n## ⚠️ %s\n\n  調べられない＝%s\n  %s\n' % (name, r.get('why'), u))
        time.sleep(1.2)
        continue
    from collections import Counter
    c = Counter((row.get('label') or row.get('status') or '?') for row in r['rows'])
    buy = sum(v for k, v in c.items() if '購入' in k or '申込' in k or '先行' in k)
    out.append('\n## %s %s\n' % ('✅' if buy else '🚨', name))
    out.append('  買える行 %d / 全%d行 … %s' % (buy, len(r['rows']),
                                              ' / '.join('%s×%d' % (k, v) for k, v in c.most_common())))
    out.append('  %s' % u)
    time.sleep(1.2)
io.open('tmp/x0920/rk_buyable.md', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/x0920/rk_buyable.md (%d件)' % len(urls))
