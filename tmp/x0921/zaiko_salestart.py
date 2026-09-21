# -*- coding: utf-8 -*-
"""ZAIKOの生データに「発売開始日時」の欄があるか全キーで確かめる。
受付前（is_sale_started=False）の153枠を載せられるかの分かれ目。
推測で日付を作らない決まりなので、**欄が本当に無いなら載せないのが正しい**。
"""
import html as H, io, json, re, sys, urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126'}

# 受付前の枠を持つイベントを、引いてあるデータから探す
d = json.load(io.open('tmp/zaiko_0921d.json', encoding='utf-8'))
targets = []
for u, e in (d.get('details') or {}).items():
    for t in e.get('tickets') or []:
        if not t.get('is_sale_started'):
            targets.append(u)
            break
out = io.open('tmp/x0921/zaiko_salestart.txt', 'w', encoding='utf-8')
out.write('受付前の枠を持つイベント %d件\n\n' % len(targets))

# その実ページを2件だけ引いて、券種の全キーを見る
for u in targets[:2]:
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
            html = r.read().decode('utf-8', 'replace')
    except Exception as e:
        out.write('取れなかった %s (%s)\n' % (u, e))
        continue
    m = re.search(r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        out.write('data-pageが無い %s\n' % u)
        continue
    ev = (json.loads(H.unescape(m.group(1))).get('props') or {}).get('event') or {}
    out.write('=== %s\n%s\n' % (u, (ev.get('name') or '')[:50]))
    for t in ev.get('tickets') or []:
        if t.get('is_sale_started'):
            continue
        out.write('  --- 受付前の券種（全キー）---\n')
        for k in sorted(t):
            v = t[k]
            if isinstance(v, dict):
                v = {kk: vv for kk, vv in v.items() if not isinstance(vv, (dict, list))}
            out.write('    %-40s = %s\n' % (k, str(v)[:130]))
        break
    out.write('\n  --- event 側の日付・販売系 ---\n')
    for k in sorted(ev):
        if re.search(r'date|time|open|start|end|status|period|sale', k, re.I):
            v = ev[k]
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)[:150]
            out.write('    %-32s = %s\n' % (k, str(v)[:150]))
    out.write('\n')
out.close()
print('wrote tmp/x0921/zaiko_salestart.txt  受付前を持つイベント %d件' % len(targets))
