# -*- coding: utf-8 -*-
"""「もう発売が始まっているのに type が『M/D HH:MM発売』のまま残っている枠」を洗い出す。
条件＝startDate <= today かつ date > today かつ type が「M/D HH:MM発売」で終わる形（not soldout）。

2026-08-16 に判明した第2の穴（ユーザーのスクショ発見）＝画面が date(締切日) に type の発売時刻を
くっつけて「〜8/23 10:00」と嘘の表示を出す。隠れ枠ヒール(startDate==date)では絶対に拾えない型。

startDate==today に限定すると「昨夜20:00発売開始」のような枠を翌朝取りこぼすので、
ここでは startDate <= today まで広げて走査する（既に「〜M/D HH:MM」形になっているものは除外）。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now()
raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))

# 「8/16 10:00発売」「8/16 10:00販売開始」等で終わる形だけが対象。
# 「〜8/23 23:59」形（変換済み）は対象外。
PAT_SALE = re.compile(r'\d{1,2}/\d{1,2}\s*(\d{1,2}):(\d{2})\s*(発売|販売開始|受付開始)\s*$')

rows = []
for e in EVENTS:
    hit = []
    for t in e.get('tickets') or []:
        sd, d, ty = t.get('startDate'), t.get('date') or '', t.get('type') or ''
        if not sd or t.get('soldout'):
            continue
        if sd <= TODAY and d > TODAY and PAT_SALE.search(ty):
            # 今日発売の枠は「発売時刻を過ぎているか」を見る（過ぎる前に叩いても締切は出ない）
            passed = True
            if sd == TODAY:
                m = PAT_SALE.search(ty)
                start_t = NOW.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
                passed = NOW >= start_t
            hit.append((t, passed))
    if hit:
        rows.append((e, hit))

done = [(e, h) for e, h in rows if all(p for _, p in h)]
wait = [(e, h) for e, h in rows if not all(p for _, p in h)]

print("=== 発売時刻を過ぎている＝今すぐ直せる: %d件 / %d枠 ===" % (
    len(done), sum(len(h) for _, h in done)))
for e, hit in done:
    print("id%-5s %-28s %s" % (e['id'], (e.get('artist') or '')[:26], (e.get('links') or {}).get('pia') or ''))
    for t, _ in hit:
        print("      - %s | date=%s | start=%s" % (t.get('type'), t.get('date'), t.get('startDate')))
print()
print("ids=" + ",".join(str(e['id']) for e, _ in done))
print()
print("=== まだ発売時刻前＝昼以降に回す: %d件 ===" % len(wait))
for e, hit in wait:
    for t, p in hit:
        if not p:
            print("id%-5s %-26s %s | date=%s" % (e['id'], (e.get('artist') or '')[:24], t.get('type'), t.get('date')))
