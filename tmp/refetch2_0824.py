# -*- coding: utf-8 -*-
"""「カードは出るのに買える枠が0」の8件を、ぴあから枠を取り直して足す（2026-08-24 朝）。

背景＝reconcile_pia --ids で MISSING 23枠。どれも先行/プレリザーブが 8/23 に終わって、
ぴあ側では次の受付が始まっているのに登録に入っていない型。

🚨 build_pia_entries に複数URLをまとめて渡すと2本目以降の枠に ticket.url が付かず
   「その枠を売っていないページ」に飛ぶ（feedback_build_pia_multiurl_loses_ticket_url）。
   → **URLを1本ずつ渡して**、そのURLが links.pia と違う時だけ ticket.url に刻む。

🚨 既存の枠は1つも消さない（足すだけ）。build_pia_entries は行を潰すので、
   まるごと置換すると手で分けた枠が畳まれる（feedback_dedup_badges_keeps_urls）。

使い方:
  python tmp/zb_refetch_0824.py            # 取得して差分を見るだけ
  python tmp/zb_refetch_0824.py --apply    # index.html に足す
"""
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
CACHE = 'tmp/zb_refetch2_0824_cache.json'
IDS = [5097, 5101]


def canon(u):
    """ぴあの2つのホスト表記を揃える。ぴあ以外は触らない。"""
    if not u:
        return None
    if 't.pia.jp' not in u and 'ticket.pia.jp' not in u:
        return u
    m = re.search(r'(eventCd|eventBundleCd)=(\w+)', u)
    if not m:
        return u
    return 'https://t.pia.jp/pia/event/event.do?%s=%s' % (m.group(1), m.group(2))


def load_events():
    src = io.open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    return src, m, json.loads(m.group(2))


def slot_key(t):
    """同じ枠かどうかの照合キー。文言・締切・発売日で見る。"""
    return (t.get('type') or '', t.get('date') or '', t.get('startDate') or '')


def fetch(events_by_id):
    """エントリごとに、紐づく全ぴあURLを1本ずつ再導出する。"""
    out = {}
    for eid in IDS:
        e = events_by_id[eid]
        base = canon((e.get('links') or {}).get('pia'))
        urls = []
        if base:
            urls.append(base)
        for t in e.get('tickets') or []:
            u = canon(t.get('url'))
            if u and u not in urls:
                urls.append(u)
        got = []
        for u in urls:
            cand = [{'newid': 900000 + eid, 'artist': e.get('artist') or '', 'urls': [u]}]
            io.open('tmp/_zb_one.json', 'w', encoding='utf-8').write(
                json.dumps(cand, ensure_ascii=False))
            r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/_zb_one.json'],
                               capture_output=True)
            if r.returncode != 0:
                print('!! id=%d %s 取得失敗' % (eid, u))
                continue
            try:
                built = json.loads(r.stdout.decode('utf-8'))
            except Exception as ex:
                print('!! id=%d %s パース失敗 %s' % (eid, u, ex))
                continue
            for b in built:
                for t in b.get('tickets') or []:
                    # このURLが links.pia と違う＝別の売り場から来た枠なので飛び先を刻む
                    if u != base and not t.get('url'):
                        t['url'] = u
                    got.append(t)
        out[str(eid)] = got
        print('id=%-5d URL%d本 → %d枠' % (eid, len(urls), len(got)))
    json.dump(out, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return out


def main():
    apply = '--apply' in sys.argv
    src, m, events = load_events()
    by = {e['id']: e for e in events}

    if os.path.exists(CACHE) and '--refetch' not in sys.argv:
        got = json.load(io.open(CACHE, encoding='utf-8'))
        print('(キャッシュ %s を使用。取り直すなら --refetch)' % CACHE)
    else:
        got = fetch(by)

    added_total = 0
    report = []
    for eid in IDS:
        e = by[eid]
        have = {slot_key(t) for t in e.get('tickets') or []}
        add = [t for t in got.get(str(eid), []) if slot_key(t) not in have]
        if not add:
            report.append('id=%-5d %-24s 追加なし' % (eid, (e.get('artist') or '')[:24]))
            continue
        report.append('id=%-5d %-24s +%d枠' % (eid, (e.get('artist') or '')[:24], len(add)))
        for t in add:
            report.append('        + %s | 〆%s | url=%s' % (t.get('type'), t.get('date'), t.get('url')))
        added_total += len(add)
        if apply:
            e.setdefault('tickets', []).extend(add)

    print('\n'.join(report))
    print('\n=== 追加 %d枠 / 対象 %d件 ===' % (added_total, len(IDS)))

    if not apply:
        print('(--apply で書き込み)')
        return 0

    nl = '\r\n' if '\r\n' in src else '\n'
    shutil.copy(PATH, PATH + '.bak_0824_missing2')
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('書き込み完了（backup: %s.bak_0824_missing2）' % PATH)
    return 0


if __name__ == '__main__':
    sys.exit(main())
