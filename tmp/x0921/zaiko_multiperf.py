# -*- coding: utf-8 -*-
"""エージェントが挙げた「1ページに複数公演」5件を、生データで確かめる。
20681 金沢「40000」／20802 新しい学校のリーダーズ／20831／20871／20872。
券種名に別の日付・会場が入っているなら、同じ公演日で並べるのは嘘になる。
"""
import html as H, io, json, re, sys, urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126'}
IDS = [20681, 20802, 20831, 20871, 20872]

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}
out = io.open('tmp/x0921/zaiko_multiperf.txt', 'w', encoding='utf-8')

for i in IDS:
    e = ev.get(i)
    if not e:
        out.write('id%s は無い\n\n' % i)
        continue
    u = (e.get('links') or {}).get('zaiko')
    out.write('=== id%s %s\n    %s @ %s 公演%s\n    %s\n'
              % (i, (e.get('name') or '')[:50], (e.get('artist') or '')[:30],
                 e.get('venue'), e.get('date'), u))
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r:
            html = r.read().decode('utf-8', 'replace')
        d = json.loads(H.unescape(re.search(
            r'<script[^>]*data-page="app"[^>]*>(.*?)</script>', html, re.S).group(1)))
        z = (d.get('props') or {}).get('event') or {}
    except Exception as ex:
        out.write('    取れなかった (%s)\n\n' % ex)
        continue
    dp = z.get('display_date_period') or {}
    out.write('    ページの会期: %s\n' % json.dumps(
        {k: (v.get('datetime_string') if isinstance(v, dict) else v) for k, v in dp.items()},
        ensure_ascii=False)[:180])
    out.write('    券種（ref_name / 受付期間 / 価格）:\n')
    for t in z.get('tickets') or []:
        osf = (t.get('on_sale_from') or {}).get('datetime_string')
        osu = (t.get('on_sale_until') or {}).get('datetime_string')
        lsd = (t.get('lottery_start_date') or {}).get('datetime_string')
        led = (t.get('lottery_end_date') or {}).get('datetime_string')
        ov = (t.get('override_datetime_period') or {}).get('datetime_string')
        out.write('      %-42s %s / 先着%s〜%s 抽選%s〜%s\n        公演の上書き=%s\n'
                  % ((t.get('ref_name') or '')[:42], t.get('display_price'),
                     osf, osu, lsd, led, ov))
    out.write('\n')
out.close()
print('wrote tmp/x0921/zaiko_multiperf.txt')
