# -*- coding: utf-8 -*-
"""X投稿に出す193組の名前でぴあを総ざらいして出た取りこぼしを入れる（2026-09-23 夜）。
day 第4便8＝「投稿に出したアーティスト名でぴあを検索して枠を全部出し、登録と突合する」。
🚨ぴあのツアーまとめ(bundle)に出てこない公演がある＝[[feedback_pia_bundle_hides_shows]]。

仕分け（会場一致と既存の作りで機械的に決めた・tmp/x0923/merge_decide 相当）:
  足し込み2件＝90012 ミュージカル『南くんの恋人』→id7335（会場も千秋楽も一致）
                90014 ロッケンロー★サミット2026 の配信視聴券→id4139（同じイベントの配信枠）
  新規11件＝既存エントリのツアー会場一覧にその会場が無い／既存が会場ごとに別エントリの作り。
            ぴあ由来なのでジャンルまで振り分ける（ビルダーの_genreをそのまま写す）。
使い方: python tmp/x0923/apply_audit_0923.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
SCR = r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\211b8b3d-6701-4434-8b7f-224ce869b3f9\scratchpad"
MERGE = {90012: 7335, 90014: 4139}          # 仮id → 足し込み先
NEWID = {90002: 22534, 90003: 22535, 90004: 22536, 90005: 22537, 90006: 22538,
         90007: 22539, 90008: 22540, 90009: 22541, 90010: 22542, 90013: 22543,
         90015: 22544}

built = {e['id']: e for e in json.load(io.open(SCR + r"\built_audit.json", encoding='utf-8'))}
text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)
by = {e.get('id'): e for e in events}

log = []
n_slot = 0
for src, dst in MERGE.items():
    b = built.get(src)
    ev = by.get(dst)
    if b is None or ev is None:
        log.append('⚠️ %s→%s が見つからない' % (src, dst))
        continue
    have = set(((t.get('type') or ''), t.get('date')) for t in (ev.get('tickets') or []))
    add = 0
    for t in (b.get('tickets') or []):
        k = ((t.get('type') or ''), t.get('date'))
        if k in have:
            continue
        t = dict(t)
        if not t.get('url'):
            t['url'] = (b.get('links') or {}).get('pia') or (ev.get('links') or {}).get('pia')
        ev.setdefault('tickets', []).append(t)
        have.add(k)
        add += 1
    if add:
        ev['verifiedAt'] = '2026-09-23'
        n_slot += add
        log.append('✅ 足し込み id=%-6s +%d枠 %s' % (dst, add, (ev.get('name') or '')[:32]))

n_new = 0
for src, newid in NEWID.items():
    b = built.get(src)
    if b is None:
        log.append('⚠️ %s が組み上がっていない' % src)
        continue
    if newid in by:
        log.append('⏭️ id=%s は既にある' % newid)
        continue
    b = dict(b)
    b['id'] = newid
    g = b.pop('_genre', None)
    b.pop('_extraGenres', None)
    b.pop('_srcgenre', None)
    if g:
        b['genre'] = g
    events.append(b)
    n_new += 1
    log.append('✅ 新規 id=%-6s genre=%-9s %s ／ %s' % (
        newid, b.get('genre'), (b.get('name') or '')[:30], (b.get('venue') or '')[:26]))

log.append('--- 足し込み %d枠 / 新規 %d件（エントリ %d件に）---' % (n_slot, n_new, len(events)))
io.open('tmp/x0923/apply_audit_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
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
