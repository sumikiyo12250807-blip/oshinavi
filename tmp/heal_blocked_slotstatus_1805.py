# -*- coding: utf-8 -*-
"""止まった26件の「消える側」の枠を、ぴあの実ページで1枠ずつ見る（2026-09-14 夜）。
取り直しに入らなかった＝ぴあで「買える」に出ていない。売り切れ（予定枚数終了）か、販売終了か、
それとも読み落としか、を枠ごとに分ける。書き込みはしない。
  ・売り切れの印付き・ぴあ以外（e+/楽天）・締切が今日より前の枠は見ない
  ・枠の飛び先（eventCd 等）を開き、公演日（と県）が合う行の状態と文言を出す
  ・飛び先が空の枠はエントリのぴあURLを順に開く
ぴあは同時2本まで＝1本ずつ・間を空けて叩く。
使い方: python tmp/heal_blocked_slotstatus_1805.py [id,id,...]   （省略時は tmp/heal_blocked_hold_1805.txt）
出力: tmp/heal_blocked_slotstatus_1805.md
"""
import datetime
import io
import json
import re
import subprocess
import sys
import time

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today()
TS = TODAY.isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
by = {e['id']: e for e in json.loads(m.group(1))}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}
arg = sys.argv[1] if len(sys.argv) > 1 else io.open('tmp/heal_blocked_hold_1805.txt', encoding='utf-8').read()
ids = [int(x) for x in arg.split(',') if x.strip()]
OTHER = re.compile(r'(eplus\.jp|rakuten|l-tike\.com|lawson)')
_cache = {}


def rows_of(url):
    if url in _cache:
        return _cache[url]
    time.sleep(2)
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    try:
        v = json.loads(r.stdout.decode('utf-8', 'replace')) if r.returncode == 0 else None
    except json.JSONDecodeError:
        v = None
    _cache[url] = v
    return v


def perf_range(ty):
    """券種名の（…公演）から公演日の幅と県を取る。R9年は2027、年が無い日は今日より前なら翌年。"""
    pk = H.perf_key(ty)
    ds = []
    for mm in re.finditer(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', pk):
        y = 2027 if mm.group(1) else TODAY.year
        d = datetime.date(y, int(mm.group(2)), int(mm.group(3)))
        if not mm.group(1) and d < TODAY - datetime.timedelta(days=60):
            d = datetime.date(y + 1, d.month, d.day)
        ds.append(d.isoformat())
    prefs = re.split(r'[・/／]', re.sub(r'\s.*$', '', pk)) if ds else []
    return (ds[0], ds[-1]) if ds else (None, None), [p.replace('県', '').replace('都', '').replace('府', '') for p in prefs if p]


out, summary = [], {}
for i in ids:
    e, o = by.get(i), built.get(i)
    if not e or not o:
        continue
    new_keys = {H.slot_key(t) for t in o.get('tickets') or [] if H.visible_slot(t, TS)}
    lost = [t for t in e.get('tickets') or [] if H.visible_slot(t, TS) and H.slot_key(t) not in new_keys
            and not t.get('soldout') and not OTHER.search(t.get('url') or '') and (t.get('date') or '') >= TS]
    out.append('## id%s %s' % (i, e.get('name')))
    if not lost:
        out.append('  （見る枠なし＝売り切れ印・ぴあ以外・締切切れだけ）\n')
        continue
    for t in lost:
        (a, b), prefs = perf_range(t.get('type'))
        urls = [t['url']] if t.get('url') else H.pia_urls(e)
        hits, readable = [], False
        for u in urls:
            rs = rows_of(u)
            if rs is None:
                continue
            readable = True
            for r in rs:
                pd = r.get('perfdate') or ''
                if a and not (a <= pd <= b):
                    continue
                if prefs and r.get('pref') and not any(p and p in r['pref'] for p in prefs):
                    continue
                hits.append(r)
            if hits:
                break
        # 券種の頭の言葉（一般発売・プレリザーブ等）で絞る＝同じ公演日の抽選や別券種の行を混ぜない
        mw = re.search(r'(先着一般発売|一般発売|一般販売|プリセール|先行先着|プレリザーブ|\d次受付|追加席発売|先行)', t.get('type') or '')
        if mw and hits:
            narrowed = [r for r in hits if mw.group(1) in (r.get('title') or '')]
            if narrowed:
                hits = narrowed
            else:
                out.append('    （券種名「%s」の行が無い＝日付と県だけで合わせた）' % mw.group(1))
        kinds = sorted({'%s｜%s｜%s｜%s｜%s' % (r['state'], r.get('statustext'), r.get('when'), r.get('venue'), (r.get('title') or '')[:40]) for r in hits})
        if not readable:
            verdict = '読めない'
        elif not hits:
            verdict = '該当行なし'
        elif all(re.search(r'(予定枚数|完売|売り?切)', r.get('statustext') or '') for r in hits):
            verdict = '売り切れ'
        elif any(r['state'] in ('受付中', '発売前') for r in hits):
            verdict = '買える行あり'
        else:
            verdict = '販売終了ほか'
        summary[verdict] = summary.get(verdict, 0) + 1
        out.append('- [%s] %s ｜締切 %s｜%s' % (verdict, t.get('type'), t.get('date'), H._url_id(t.get('url'))))
        out += ['    ・' + k for k in kinds[:6]]
    out.append('')
    print('id%s 済' % i)
io.open('tmp/heal_blocked_slotstatus_1805.md', 'w', encoding='utf-8').write('\n'.join(out))
print('まとめ:', '／'.join('%s %d' % kv for kv in sorted(summary.items())))
print('書き出し tmp/heal_blocked_slotstatus_1805.md')
