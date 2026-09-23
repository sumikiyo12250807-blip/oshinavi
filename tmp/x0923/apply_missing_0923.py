# -*- coding: utf-8 -*-
"""ぴあの「明日〜3日後発売」突き合わせで出た抜けを直す（2026-09-23 夜・X投稿の文面を見せる前）。
[[feedback_existing_entries_miss_new_windows]]＝登録済みエントリに、ぴあが後から足した会場・先行が入らない。

未登録4件（新しく足す・ぴあ由来なのでジャンルまで振り分ける）:
  22530 渋谷慶一郎 jpop / 22531 カウントダウン ミュージカル musical
  22532 舞台『魔法使いの約束』…Orchestra Concert engeki / 22533 東京アマデウス管弦楽団 classic
足し込み4件（既存へ枠だけ足す・足し算で既存は消さない）:
  5713 ワンワンまつり / 7751 山里亮太の140 石川 / 11115 太陽生命ラグビー / 21142 NHK交響楽団 in ICHIKAWA
使い方: python tmp/x0923/apply_missing_0923.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
SCR = r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\211b8b3d-6701-4434-8b7f-224ce869b3f9\scratchpad"
NEW_GENRE = {22530: 'jpop', 22531: 'musical', 22532: 'engeki', 22533: 'classic'}

miss = json.load(io.open(SCR + r"\built_miss.json", encoding='utf-8'))
fill = {e['id']: e for e in json.load(io.open(SCR + r"\built_fill.json", encoding='utf-8'))}

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)
by = {e.get('id'): e for e in events}

log = []
# ① 足し込み
n_slot = 0
for i, b in fill.items():
    ev = by.get(i)
    if ev is None:
        log.append('⚠️ id=%s が見つからない' % i)
        continue
    have = set(((t.get('type') or ''), t.get('date')) for t in (ev.get('tickets') or []))
    add = 0
    for t in (b.get('tickets') or []):
        k = ((t.get('type') or ''), t.get('date'))
        if k in have:
            continue
        t = dict(t)
        if not t.get('url'):
            t['url'] = (ev.get('links') or {}).get('pia')
        ev.setdefault('tickets', []).append(t)
        have.add(k)
        add += 1
    if add:
        ev['verifiedAt'] = '2026-09-23'
        n_slot += add
        log.append('✅ 足し込み id=%-6s +%d枠 %s' % (i, add, (ev.get('name') or '')[:30]))

# ② 新規（ジャンルまで振り分けて足す）
n_new = 0
exist = set(by)
for b in miss:
    i = b.get('id')
    if i in exist:
        log.append('⏭️ id=%s は既にある' % i)
        continue
    b = dict(b)
    g = NEW_GENRE.get(i)
    if g:
        b['genre'] = g
        b.pop('_genre', None)
        b.pop('_extraGenres', None)
        b.pop('_srcgenre', None)
    events.append(b)
    n_new += 1
    log.append('✅ 新規 id=%-6s genre=%-8s %s' % (i, b.get('genre'), (b.get('name') or '')[:34]))

log.append('--- 足し込み %d枠 / 新規 %d件（エントリ %d件に）---' % (n_slot, n_new, len(events)))
io.open('tmp/x0923/apply_missing_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
sys.stdout.write('done: +%d slots / +%d entries\n' % (n_slot, n_new))
if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open('index.html', 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
