# -*- coding: utf-8 -*-
"""「〆切日に発売時刻がくっつく」型のうち e+ 由来の枠を、各公演の -P 個別ページから
正しい受付終了日時で取り直す（判定のみ・結果は tmp/eplus_fix_0817.json）。

対象＝ぴあURLが無く、枠に e+ の個別URLがあり、type が「M/D HH:MM発売」で終わる形。
画面が date(締切日) に type の発売時刻をくっつけて「〜9/20 20:00」と嘘を出すのを止める。
"""
import re, json, sys, io, time, subprocess, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
IDS = [77, 3017, 3018, 3019, 3020, 3023, 3024, 3026, 3027, 3028, 3029, 3030, 3031,
       3032, 3034, 3036, 3037, 3039, 3041, 3042, 3044, 3045, 3049, 3055, 3056,
       3058, 3102, 3065]

PAT_SALE = re.compile(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*(発売|販売開始|受付開始)\s*$')
# eplus_detail.py の1行  例:「受付期間:2026/7/30(木)10:00～2026/11/14(土)18:00」
PAT_WIN = re.compile(
    r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})'
    r'[～~](\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')

raw = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))

targets = []
for e in EV:
    if e['id'] not in IDS:
        continue
    for t in e.get('tickets') or []:
        if t.get('soldout'):
            continue
        ty, d, sd = t.get('type') or '', t.get('date') or '', t.get('startDate')
        if not sd or sd > TODAY or d <= TODAY:
            continue
        if not PAT_SALE.search(ty):
            continue
        u = t.get('url') or (e.get('links') or {}).get('eplus') or ''
        if 'eplus.jp' not in u:
            continue
        targets.append((e['id'], e.get('artist', ''), ty, d, sd, u))

print('対象 %d枠' % len(targets))
out = []
for i, (eid, name, ty, d, sd, url) in enumerate(targets, 1):
    r = subprocess.run([sys.executable, 'tools/eplus_detail.py', url],
                       capture_output=True, text=True, encoding='utf-8', timeout=180)
    txt = r.stdout or ''
    wins = []
    for line in txt.split('\n'):
        if '受付中' not in line:
            continue
        m = PAT_WIN.search(line)
        if m:
            g = [int(x) for x in m.groups()[:5]] + [int(x) for x in m.groups()[5:]]
            sdt = '%04d-%02d-%02d' % (g[0], g[1], g[2])
            edt = '%04d-%02d-%02d' % (g[5], g[6], g[7])
            wins.append({'sd': sdt, 'ed': edt, 'ed_time': '%d:%02d' % (g[8], g[9]),
                         'line': line.strip()})
    # 登録の date と終了日が一致する窓を優先。無ければ受付中の窓のうち終了が一番遅いもの。
    pick = next((w for w in wins if w['ed'] == d), None)
    if pick is None and wins:
        pick = max(wins, key=lambda w: (w['ed'], w['ed_time']))
    out.append({'id': eid, 'name': name, 'type': ty, 'date': d, 'startDate': sd,
                'url': url, 'wins': wins, 'pick': pick})
    print('[%d/%d] id%s %s → %s' % (
        i, len(targets), eid, ty[:40],
        ('%s %s' % (pick['ed'], pick['ed_time'])) if pick else 'MISS(受付中の窓なし)'), flush=True)
    time.sleep(1.5)

io.open('tmp/eplus_fix_0817.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('\nwrote tmp/eplus_fix_0817.json')
ok = [o for o in out if o['pick'] and o['pick']['ed'] == o['date']]
diff = [o for o in out if o['pick'] and o['pick']['ed'] != o['date']]
miss = [o for o in out if not o['pick']]
print('日付一致 %d / 日付ズレ %d / 窓なし %d' % (len(ok), len(diff), len(miss)))
for o in diff:
    print('  ズレ id%s %s | 登録%s ≠ e+%s %s' % (o['id'], o['type'][:36], o['date'],
                                              o['pick']['ed'], o['pick']['ed_time']))
for o in miss:
    print('  窓なし id%s %s | %s' % (o['id'], o['type'][:36], o['url']))
