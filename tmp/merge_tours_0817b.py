# -*- coding: utf-8 -*-
"""同じアーティスト・同じツアーが2エントリに分かれているものを1エントリに統合する。
[[feedback_tour_consolidate]]（ツアーは1エントリ）／[[feedback_tour_per_ticket_url]]（会場ごとに
eventCd が違うので各ticketに会場別urlを必ず付ける。無いと全バッジが1会場のページに飛ぶ）。

🚨 CRLF保持：newline='' で読み書きし、作り直した部分は \\n を \\r\\n に戻す
   （[[feedback_index_html_crlf_preserve]]＝json.dumps で作り直した所だけLFになる罠）。

  python tmp/merge_tours_0817b.py           … 判定のみ
  python tmp/merge_tours_0817b.py --apply   … 適用
"""
import io, re, sys, json, datetime
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PAIRS = [(4436, 4446), (4450, 4477), (4455, 4478)]   # (残す, 吸収する)
WD = '月火水木金土日'

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
before_lf = src.count('\n')

BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)


def blocks(text):
    return {int(m.group(1)): m for m in BLOCK.finditer(text)}


def ymd(s):
    return datetime.date(*[int(x) for x in s.split('-')])


def label(d):
    return '%d年%d月%d日(%s)' % (d.year, d.month, d.day, WD[d.weekday()])


def dump_entry(obj):
    """エントリ1件を index.html の体裁（2字下げの { , 4字下げのフィールド）で文字列化。"""
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    body = '\n'.join(('  ' + ln) if ln else ln for ln in body.split('\n'))
    return body.replace('\n', '\r\n')


report = []
for keep, absorb in PAIRS:
    bl = blocks(src)
    if keep not in bl or absorb not in bl:
        print('⚠️ id%d / id%d のどちらかが見つからない（既に処理済み？）' % (keep, absorb))
        continue
    A = json.loads(bl[keep].group(0).rstrip(',').strip())
    B = json.loads(bl[absorb].group(0).rstrip(',').strip())

    urlA = (A.get('links') or {}).get('pia')
    urlB = (B.get('links') or {}).get('pia')
    if not urlA or not urlB or urlA == urlB:
        print('⚠️ id%d/id%d のぴあURLが取れない or 同一。統合を見送る' % (keep, absorb))
        continue

    # ①各ticketに会場別URLを付ける（これが無いと全バッジが片方の会場に飛ぶ）
    for t in A.get('tickets') or []:
        t.setdefault('url', urlA)
    for t in B.get('tickets') or []:
        t.setdefault('url', urlB)

    # ②統合
    dA, dB = ymd(A['date']), ymd(B['date'])
    lo, hi = (dA, dB) if dA <= dB else (dB, dA)
    prefs = [p for p in [A.get('prefecture', ''), B.get('prefecture', '')] if p]
    venues = [v for v in [A.get('venue', ''), B.get('venue', '')] if v]

    merged = dict(A)
    merged['tickets'] = (A.get('tickets') or []) + (B.get('tickets') or [])
    merged['date'] = hi.isoformat()
    merged['prefecture'] = '・'.join(prefs)
    merged['venue'] = '全国ツアー（%s）' % '／'.join(venues)
    merged['dateLabel'] = '%s〜%s %s' % (label(lo), label(hi), merged['prefecture'])

    # ③置換（残す方）と削除（吸収する方）
    src = src[:bl[keep].start()] + dump_entry(merged) + \
        (',' if bl[keep].group(0).endswith(',') else '') + src[bl[keep].end():]

    bl = blocks(src)
    m = bl[absorb]
    end = m.end()
    while end < len(src) and src[end:end + 2] == '\r\n':
        end += 2
        break
    src = src[:m.start()] + src[end:]

    report.append((keep, absorb, merged['venue'], merged['prefecture'],
                   merged['dateLabel'], len(merged['tickets'])))

# ④NEW_ORDER から吸収した側を外す
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', src)
order = json.loads(mo.group(2))
removed = [b for _, b in PAIRS if b in order]
order = [i for i in order if i not in removed]
src = src[:mo.start(2)] + json.dumps(order) + src[mo.end(2):]

print('=== ツアー統合 %d組 ===' % len(report))
for keep, absorb, venue, pref, dl, n in report:
    print('  id%-5d ← id%-5d  枠%d本' % (keep, absorb, n))
    print('     venue      %s' % venue)
    print('     prefecture %s' % pref)
    print('     dateLabel  %s' % dl)
print('\nNEW_ORDER から外した: %s（残り %d件）' % (removed, len(order)))

# ⑤検算
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
print('EVENTS 件数 %d / 新着プール %d件' % (len(EV), len([e for e in EV if e.get('genre') == 'new'])))
print('CRLF %d → %d ／ LF単独 %d → %d' % (before_crlf, src.count('\r\n'),
                                          before_lf - before_crlf, src.count('\n') - src.count('\r\n')))
bad = [e['id'] for e in EV if e.get('genre') == 'new' and len({t.get('url') for t in e.get('tickets') or []}) > 1
       and any(not t.get('url') for t in e.get('tickets') or [])]
print('urlの付け漏れ:', bad or 'なし')

if APPLY:
    io.open('index.html.bak_0817b_merge', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('\n適用しました（backup: index.html.bak_0817b_merge）')
else:
    print('\n（判定のみ。適用するなら --apply）')
