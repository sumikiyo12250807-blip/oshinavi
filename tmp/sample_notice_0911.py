# -*- coding: utf-8 -*-
"""既存エントリのぴあページを抜き取りで開き、「告知文にだけ出ている先行」がどれくらい埋もれているか数える（読むだけ）。
・対象＝公演日が今日以降で links.pia を持つエントリから、決まった順（id）で等間隔に N件
・受付期間の締切が今日より前のものは「もう終わった」として別に数える
使い方: python tmp/sample_notice_0911.py [N=200]
出力: tmp/sample_notice_0911.md
"""
import datetime, io, json, re, sys, time
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
TODAY = datetime.date.today()
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
pool = sorted([e for e in ev if (e.get('date') or '') >= TODAY.isoformat() and (e.get('links') or {}).get('pia')],
              key=lambda e: e['id'])
step = max(1, len(pool) // N)
pick = pool[::step][:N]


def end_date(per):
    m = re.findall(r'(\d{1,2})/(\d{1,2})', per)
    if not m:
        return None
    mo, d = map(int, m[-1])
    y = TODAY.year + (1 if mo < TODAY.month - 3 else 0)
    return datetime.date(y, mo, d)


hits, live, err = [], 0, 0
for i, e in enumerate(pick, 1):
    u = e['links']['pia']
    try:
        h = B.fetch(u)
    except Exception:
        err += 1
        continue
    items, urls = B.find_notice_presales(h)
    if items:
        alive = [x for x in items if (end_date(x[1]) or TODAY) >= TODAY]
        live += 1 if alive else 0
        hits.append((e['id'], e.get('name'), u, items, urls, bool(alive)))
    if i % 25 == 0:
        print('[%d/%d] 告知文先行あり %d（うち受付がまだ終わっていない %d）' % (i, len(pick), len(hits), live))
    time.sleep(1.0)
with io.open('tmp/sample_notice_0911.md', 'w', encoding='utf-8') as f:
    f.write('# 告知文にだけ出ている先行の抜き取り（%s）\n\n' % TODAY)
    f.write('母集団＝公演が今日以降でぴあリンクを持つ %d件 ／ 抜き取り %d件 ／ 取得失敗 %d件\n\n' % (len(pool), len(pick), err))
    f.write('告知文先行あり **%d件**（うち受付がまだ終わっていない **%d件**）\n\n' % (len(hits), live))
    for i, n, u, items, urls, a in hits:
        f.write('- %s id%s %s\n  - %s\n' % ('🟢' if a else '⚪', i, n, u))
        for nm, per in items:
            f.write('  - ■%s 受付期間：%s\n' % (nm, per))
        for vu in urls[:3]:
            f.write('  - 申込: %s\n' % vu)
print('抜き取り %d件 ／ 告知文先行あり %d件（生きている %d件）／ 取得失敗 %d件 → tmp/sample_notice_0911.md'
      % (len(pick), len(hits), live, err))
