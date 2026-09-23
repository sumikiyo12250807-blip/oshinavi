# -*- coding: utf-8 -*-
"""TIGETの「名前×公演日が既存と一致」した件を、**既存エントリに枠を足す**（2026-09-23 夜）。

inject_tiget が止めた8件のうち7件は、同じ公演の**別売り場／別券種（再販・第2弾）**だった。
足すだけ＝既存の枠は1つも消さない（[[feedback_capture_all_deadlines_on_add]]／
[[feedback_dedup_badges_keeps_urls]]＝飛び先が違えば畳まない）。

⛔ **Blueberry Girlsツアー直前無銭ライブ（9/27 福岡）は入れない**＝足し先候補が
   id12156「この映画を見終わったら 福岡公演」で**イベント名が違う**（出演者名での一致に見える）。
   別件として調べる。

使い方: python tmp/x0923/tiget_merge7.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

# TIGETのイベント番号 → 足し先の既存id（tmp/x0923/tiget_rest8.txt で1件ずつ突き合わせた）
MERGE = {
    '524590': 6263,    # KOKOKARA FES 大阪10/3 … 既存はe+枠だけ。TIGETでも売っている
    '513658': 5870,    # いのちのうた 第19章 福岡10/12 … 既存はぴあ枠だけ
    '519928': 7857,    # 松谷卓 ピアノアルバムライブ 愛媛11/29 … 既存はぴあ枠だけ
    '524427': 12600,   # trick or melody【再販2部Aチケット】→ Aチケットのエントリ
    '524428': 12602,   # 【1部再販Bチケット】→ 【1部】Bチケットのエントリ
    '524430': 12603,   # 【2部再販Bチケット】→ 【2部】Bチケットのエントリ
    '524141': 12847,   # 第二回GMUボーリング大会 青森10/25 … 既存7枠は9/18締切・こちらは9/24発売の第2弾
}

text = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)
by = {e['id']: e for e in events}

built = json.load(io.open('tmp/built_tiget_0923pm.json', encoding='utf-8'))
if isinstance(built, dict):
    built = built.get('entries') or []
src = {}
for e in built:
    for n in re.findall(r'/events/(\d+)', (e.get('links') or {}).get('tiget') or ''):
        src[n] = e

log = []
added = 0
for ev_no, dst_id in sorted(MERGE.items()):
    s = src.get(ev_no)
    d = by.get(dst_id)
    if not s or not d:
        log.append('%s → id%s ✗ 見つからない' % (ev_no, dst_id))
        continue
    have = {(t.get('type'), t.get('url')) for t in (d.get('tickets') or [])}
    news = [t for t in (s.get('tickets') or []) if (t.get('type'), t.get('url')) not in have]
    if not news:
        log.append('%s → id%s ＝足す枠なし' % (ev_no, dst_id))
        continue
    d.setdefault('tickets', []).extend(news)
    # 売り場のリンクも残す（買える場所を消さない）
    links = d.setdefault('links', {})
    if not links.get('tiget'):
        links['tiget'] = (s.get('links') or {}).get('tiget')
    added += len(news)
    log.append('%s → id%-6s ＋%d枠（%d→%d）%s'
               % (ev_no, dst_id, len(news), len(d['tickets']) - len(news), len(d['tickets']),
                  (d.get('name') or '')[:30]))
    for t in news:
        log.append('        ＋ %s' % (t.get('type') or ''))

rep = io.open('tmp/x0923/tiget_merge7.txt', 'w', encoding='utf-8')
rep.write('TIGETの足し込み ＋%d枠 / 対象%d件\n\n' % (added, len(MERGE)))
rep.write('\n'.join(log) + '\n')
rep.close()
sys.stdout.write('added_slots=%d targets=%d -> tmp/x0923/tiget_merge7.txt\n' % (added, len(MERGE)))

if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)

body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open(PATH, 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
