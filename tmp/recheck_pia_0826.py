# -*- coding: utf-8 -*-
"""新着プールの独立再照合。ぴあの実ページを subprocess で取り直し（build とは別経路）、
実ページ側から「あるべき値」を再導出してから登録値と比べる（投入値にアンカーしない）。
 1 買える枠数（受付中/発売前）
 2 千秋楽（実ページの公演日の最大）と ev.date
 3 県・会場
 4 締切/発売日（when）と ticket.date
 5 売切枠の混入
"""
import re, json, sys, time, subprocess, unicodedata, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

SRC = [a for a in sys.argv[1:] if not a.startswith('--')]
h = open(SRC[0] if SRC else 'index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
NEW = [e for e in json.loads(m.group(2)) if e.get('genre') == 'new']

# --range=5201-5250 で対象を絞る（新着プールが100件近いので50件ずつ2本に分けて回す）
_rng = [a for a in sys.argv[1:] if a.startswith('--range=')]
if _rng:
    _lo, _hi = (int(x) for x in _rng[0].split('=', 1)[1].split('-'))
    NEW = [e for e in NEW if _lo <= e['id'] <= _hi]
print("対象 %d件 (id %s〜%s)" % (len(NEW), NEW[0]['id'] if NEW else '-', NEW[-1]['id'] if NEW else '-'))


def norm(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').replace('　', '').lower()


def pia(url):
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'],
                       capture_output=True, text=True, encoding='utf-8', timeout=120)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


WHEN_END = re.compile(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})')
# when は3形＝「～ 終了日」／「開始日 ～ 終了日」／「開始日 より発売」。
# 先頭が日付で始まるものはその日付が受付開始日（＝登録の startDate に対応する）。
WHEN_ST = re.compile(r'^\s*(\d{4})/(\d{1,2})/(\d{1,2})')

bad = []
for i, e in enumerate(NEW, 1):
    url = (e.get('links') or {}).get('pia')
    if not url:
        bad.append((e['id'], e['name'], 'ぴあURLが無い'))
        continue
    rows = pia(url)
    if rows is None:
        bad.append((e['id'], e['name'], '実ページ取得できず（要再試行）'))
        time.sleep(2)
        continue
    buy = [r for r in rows if r['state'] in ('受付中', '発売前')]
    reg = e.get('tickets') or []

    # 1 枠数
    if len(buy) != len(reg):
        bad.append((e['id'], e['name'], '枠数ズレ 登録%d / 実ページ%d' % (len(reg), len(buy))))

    # 2 千秋楽（買える枠の公演日から再導出）
    ds = [d for r in buy for d in (r.get('perfdate'), r.get('perf_end')) if d]
    if ds:
        last = max(ds)
        if e.get('date') != last:
            bad.append((e['id'], e['name'], 'ev.date=%s / 実ページ千秋楽=%s' % (e.get('date'), last)))

    # 3 県・会場
    prefs = {r['pref'] for r in buy if r.get('pref')}
    if prefs and e.get('prefecture') and e['prefecture'] != '全国':
        if not any(norm(e['prefecture']) in norm(p) or norm(p) in norm(e['prefecture']) for p in prefs):
            bad.append((e['id'], e['name'], 'pref=%s / 実ページ=%s' % (e['prefecture'], '・'.join(prefs))))
    ven = {r['venue'] for r in buy if r.get('venue')}
    if ven and e.get('venue') and '全国ツアー' not in e['venue']:
        if not any(norm(v) in norm(e['venue']) or norm(e['venue']) in norm(v) for v in ven):
            bad.append((e['id'], e['name'], 'venue=%s / 実ページ=%s' % (e['venue'][:24], '・'.join(list(ven)[:2])[:34])))

    # 4 締切/発売日
    real_ends, real_starts = set(), set()
    for r in buy:
        w = r.get('when') or ''
        mm = WHEN_END.search(w)
        if mm:
            real_ends.add('%04d-%02d-%02d' % tuple(int(x) for x in mm.groups()))
        ms = WHEN_ST.search(w)
        if ms:
            real_starts.add('%04d-%02d-%02d' % tuple(int(x) for x in ms.groups()))
    reg_dates = {t.get('date') for t in reg if t.get('date')}
    reg_starts = {t.get('startDate') for t in reg if t.get('startDate')}
    unknown_end = [d for d in reg_dates if d not in real_ends and d not in real_starts]
    if real_ends and unknown_end:
        bad.append((e['id'], e['name'], '締切が実ページに無い 登録%s / 実%s'
                    % (','.join(sorted(unknown_end)), ','.join(sorted(real_ends)) or '-')))
    unknown_start = [d for d in reg_starts if d not in real_starts]
    if real_starts and unknown_start:
        bad.append((e['id'], e['name'], '発売日が実ページに無い 登録%s / 実%s'
                    % (','.join(sorted(unknown_start)), ','.join(sorted(real_starts)))))

    # 5 売切混入（登録枠名が実ページの受付終了カードと一致するか）
    dead = [r for r in rows if r['state'] == '受付終了' and re.search(r'予定枚数|完売|売り?切', r.get('statustext') or '')]
    for t in reg:
        for r in dead:
            if norm(r['title'])[:12] and norm(r['title'])[:12] in norm(t.get('type')):
                bad.append((e['id'], e['name'], '売切枠が登録に混入? %s' % (t.get('type') or '')[:34]))
    print('[%d/%d] id%s 済' % (i, len(NEW), e['id']), flush=True)
    time.sleep(2)

print()
print('=== 独立再照合の指摘: %d件 ===' % len(bad))
for eid, nm, msg in bad:
    print('  id%-5d %-30s %s' % (eid, nm[:30], msg))
