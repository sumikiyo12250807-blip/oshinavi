# -*- coding: utf-8 -*-
"""ZAIKOの個別ページの券種ごとの販売期間とフラグだけを並べる（Inertia の data-page の中身）。"""
import html, json, re, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
for u in sys.argv[1:]:
    t = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    m = re.search(r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', t, re.S)
    if not m:
        m = re.search(r'data-page="([^"]+)"', t)
    d = json.loads(html.unescape(m.group(1)))
    ev = (d.get('props') or {}).get('event') or {}
    print('■', u, '|', ev.get('name') or ev.get('title'))
    tickets = ev.get('tickets') or ev.get('ticket_types') or []
    for tk in tickets:
        print('   %s | from %s until %s | lot_end %s | sold_out %s sale_ended %s' % (
            tk.get('ref_name') or tk.get('name'), tk.get('on_sale_from'), tk.get('on_sale_until'),
            tk.get('lottery_end_date'), tk.get('is_sold_out'), tk.get('is_sale_ended')))
    if not tickets:
        print('   keys:', list(ev.keys())[:40])
