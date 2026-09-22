#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZAIKO単独エントリを、同じ公演の既存エントリ（ぴあ/楽天/e+）へ畳む。

ユーザー決定（2026-09-22夜）＝「**ぴあ優先・ボタンは全部載せる**」
＝ 既存（ぴあ側）のエントリに `links.zaiko` を足し、ZAIKO側の販売枠を
   **ticket.url に ZAIKO の個別URLを焼き込んだ上で足し込む**。ZAIKO単独エントリは消す。

🚨守ること
- 枠は**足し算**。既存の枠は1つも消さない（[[feedback_dedup_badges_keeps_urls]]＝飛び先URLが違えば畳まない）
- ZAIKO側の枠には必ず ticket.url（ZAIKOの個別URL）を焼く（[[feedback_tour_per_ticket_url]]）
- 売り切れ・販売終了の印は**そのまま持っていく**（[[feedback_soldout_keep_visible]]）
- 畳む相手は **--pairs で明示した組だけ**。自動で広げない

使い方:
  python tools/fold_zaiko_into_existing.py --pairs 20820:2965,20838:7217   # 下見
  python tools/fold_zaiko_into_existing.py --pairs ... --apply             # 実行
  python tools/fold_zaiko_into_existing.py --selftest
"""
import argparse
import io
import json
import re
import sys

sys.path.insert(0, 'tools')


def load_events(path='index.html'):
    text = io.open(path, encoding='utf-8').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    if not m:
        raise RuntimeError('const EVENTS not found')
    start = m.start(1)
    events, end = json.JSONDecoder().raw_decode(text, start)
    return text, start, end, events


def slot_key(t):
    """同じ枠かどうかの鍵＝券種名（日付部分を落とす）＋締切＋飛び先URL。
    飛び先が違えば別の枠として残す。"""
    ty = re.sub(r'\d', '', t.get('type') or '')
    return (ty, t.get('date'), t.get('url') or '')


def fold(events, pairs, log):
    by_id = {e.get('id'): e for e in events}
    drop_ids = set()
    changed = 0
    for zid, tid in pairs:
        z = by_id.get(zid)
        t = by_id.get(tid)
        if z is None or t is None:
            log.append('  ⚠️ id=%s→%s : どちらかが見つからない（z=%s t=%s）' % (zid, tid, z is not None, t is not None))
            continue
        zurl = (z.get('links') or {}).get('zaiko')
        if not zurl:
            log.append('  ⚠️ id=%s : ZAIKOのURLが無いので畳まない' % zid)
            continue
        # 1) 受け側に links.zaiko を足す（既にあれば触らない）
        links = t.setdefault('links', {})
        if not links.get('zaiko'):
            links['zaiko'] = zurl
        # 2) ZAIKO側の枠を、飛び先URLを焼いてから足す
        have = set(slot_key(x) for x in (t.get('tickets') or []))
        added = 0
        for s in (z.get('tickets') or []):
            s = dict(s)
            if not s.get('url'):
                s['url'] = zurl
            if slot_key(s) in have:
                continue
            t.setdefault('tickets', []).append(s)
            have.add(slot_key(s))
            added += 1
        drop_ids.add(zid)
        changed += 1
        log.append('  ✅ ZAIKO id=%-6s → 既存 id=%-6s  枠+%d（受け側 %d枠に）  %s' % (
            zid, tid, added, len(t.get('tickets') or []), (t.get('name') or t.get('artist') or '')[:34]))
    return drop_ids, changed


def selftest():
    """畳む処理の中身だけを、作り物のデータで確かめる。"""
    evs = [
        {'id': 1, 'name': 'X', 'links': {'pia': 'P'}, 'tickets': [
            {'type': '一般発売（東京 11/18公演）〜11/17 23:59', 'date': '2026-11-17', 'url': 'P1'}]},
        {'id': 2, 'name': 'X', 'links': {'zaiko': 'Z'}, 'tickets': [
            {'type': 'VIP（11/18 17:30公演）〜11/17 23:59', 'date': '2026-11-17'},
            {'type': 'CAT3（11/18 17:30公演）〜11/17 23:59', 'date': '2026-11-17', 'soldout': True}]},
    ]
    log = []
    drop, n = fold(evs, [(2, 1)], log)
    ok = True
    recv = evs[0]
    if recv['links'].get('zaiko') != 'Z':
        print('NG ①受け側に links.zaiko が入っていない'); ok = False
    if len(recv['tickets']) != 3:
        print('NG ②枠が足し算になっていない（%d枠）' % len(recv['tickets'])); ok = False
    if any(t.get('url') != 'Z' for t in recv['tickets'][1:]):
        print('NG ③ZAIKO側の枠に飛び先URLが焼かれていない'); ok = False
    if recv['tickets'][0].get('url') != 'P1':
        print('NG ④既存の枠の飛び先が書き換わった'); ok = False
    if not any(t.get('soldout') for t in recv['tickets']):
        print('NG ⑤売り切れの印が落ちた'); ok = False
    if drop != {2}:
        print('NG ⑥消す側のidが違う: %s' % drop); ok = False
    # 同じ枠を二度足さない
    log2 = []
    fold(evs, [(2, 1)], log2)
    if len(recv['tickets']) != 3:
        print('NG ⑦二度流すと枠が増える（%d枠）' % len(recv['tickets'])); ok = False
    print('selftest: %s' % ('全部OK' if ok else '失敗あり'))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pairs', help='ZAIKOのid:畳む先のid をカンマ区切りで（例 20820:2965,20838:7217）')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--file', default='index.html')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.pairs:
        ap.error('--pairs が要る')
    pairs = []
    for chunk in a.pairs.split(','):
        z, t = chunk.split(':')
        pairs.append((int(z), int(t)))

    text, start, end, events = load_events(a.file)
    before = len(events)
    log = ['=== ZAIKOを既存へ畳む（%d組）===' % len(pairs)]
    drop_ids, changed = fold(events, pairs, log)
    events = [e for e in events if e.get('id') not in drop_ids]
    log.append('--- 畳んだ %d組 / エントリ %d件 → %d件 ---' % (changed, before, len(events)))
    out = io.open('tmp/fold_zaiko_report.txt', 'w', encoding='utf-8')
    out.write('\n'.join(log) + '\n')
    out.close()
    print('\n'.join(log))

    if not a.apply:
        print('\n(--apply で書き込み)')
        return 0
    # 🚨 改行コードを保つ＝元の書き方（1スペース字下げ・CRLF）に合わせる
    body = json.dumps(events, ensure_ascii=False, indent=2)
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
    newtext = text[:start] + body + text[end:]
    io.open(a.file, 'w', encoding='utf-8', newline='').write(newtext)
    print('書き込み完了: %s' % a.file)
    return 0


if __name__ == '__main__':
    sys.exit(main())
