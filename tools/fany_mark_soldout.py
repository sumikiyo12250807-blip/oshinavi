# -*- coding: utf-8 -*-
"""FANYの枠に「予定数終了」＝売り切れの印を付ける（楽天の rakuten_mark_soldout に当たる道具）。

  python tools/fany_mark_soldout.py                 … 下見（tmp/fany_soldout_report.txt に出すだけ）
  python tools/fany_mark_soldout.py --apply         … index.html に書く
  python tools/fany_mark_soldout.py --ids 22821,19745 [--sleep 1.5]
  python tools/fany_mark_soldout.py --selftest

## なぜ要るか（2026-11-04 新設）

FANY の一覧（fany_harvest が読むもの）には「予定数終了」が出ない。だから build_fany_entries /
heal_fany / gate_fany_slots は売り切れを1件も拾えていなかった。売り場の受付ページ
`https://ticket.fany.lol/reception/<受付id>/<公演id>`（tickets[].url）には券種ごとに

    <p class="g-sellItems_type">前売　一般</p>      （古い形は g-sellItems_name）
    <p class="g-sellItems_state"> 予定数終了 </p>

の形で状態が出る（実例 id22821 https://ticket.fany.lol/reception/68191/29331）。

## 判定

- 対象＝ticket.fany.lol/reception の url を持つ枠で、soldout が無く、締切 date が今日以降
- その受付の券種が**全部**「予定数終了」→ soldout: true ＋ soldoutSince（今日）
- 一部だけ予定数終了 → 触らない・報告だけ
- 発売中・受付終了・販売終了 など → 触らない。見たことの無い文字は数えて報告
- 読めない（404・混雑・形が違う）→ 触らない・報告（「売り切れていない」ではなく「確かめられていない」）
- 売り切れは**消さない**（[[feedback_soldout_keep_visible]]）
"""
import argparse
import collections
import datetime
import html as H
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'index.html')
REPORT = os.path.join(ROOT, 'tmp', 'fany_soldout_report.txt')
LOCK = os.path.join(ROOT, 'tmp', 'x1104', 'index.lock')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
RE_RECEPTION = re.compile(r'https?://ticket\.fany\.lol/reception/\d+/\d+')

SOLD = '予定数終了'
# 見たことのある文字（触らない）。これ以外は「見たことの無い文字」として数える
KNOWN = {SOLD, '発売中', '受付中', '先着発売中', '受付終了', '販売終了', '発売前', '受付前',
         '抽選受付中', '残りわずか', '残りわずか!', '発売終了'}

RE_TICKET = re.compile(r'<div class="g-sellItems_ticket">(.*?)</div>', re.S)
RE_TYPE = re.compile(r'<p class="g-sellItems_(?:type|name)">(.*?)</p>', re.S)
RE_STATE = re.compile(r'<p class="g-sellItems_state">(.*?)</p>', re.S)


def clean(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return re.sub(r'[ \t\r\n]+', ' ', H.unescape(s)).strip(' \t\r\n')   # 全角スペースは残す


def parse(page):
    """受付ページ → [(券種, 状態)]。券種の箱が無ければ state だけを拾う。"""
    out = []
    for blk in RE_TICKET.findall(page):
        st = RE_STATE.search(blk)
        if not st:
            continue
        ty = RE_TYPE.search(blk)
        out.append((clean(ty.group(1)) if ty else '', clean(st.group(1))))
    if not out:
        out = [('', clean(s)) for s in RE_STATE.findall(page)]
    return out


def judge(items):
    """'all' / 'part' / 'none' / None（読めない）。"""
    if not items:
        return None
    n = sum(1 for _, s in items if s == SOLD)
    if n == len(items):
        return 'all'
    return 'part' if n else 'none'


def fetch(url, tries=3):
    last = ''
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace'), None
        except urllib.error.HTTPError as ex:
            last = 'HTTP %s' % ex.code
            if ex.code == 404:
                break
        except Exception as ex:  # noqa: BLE001
            last = repr(ex)[:70]
        time.sleep(3 * (i + 1))
    return None, last


def take_lock():
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    waited = 0
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, ('fany_mark_soldout pid=%d\n' % os.getpid()).encode())
            os.close(fd)
            return
        except FileExistsError:
            if waited % 30 == 0:
                print('index.lock 待ち… %d秒' % waited)
            time.sleep(2)
            waited += 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=1.5)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date.today().isoformat()
    only = {int(x) for x in re.findall(r'\d+', a.ids)}
    h = io.open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    events = json.loads(m.group(2))

    # 対象の枠（url ごとにまとめる）
    by_url = collections.OrderedDict()
    for e in events:
        if only and e['id'] not in only:
            continue
        for t in e.get('tickets') or []:
            mu = RE_RECEPTION.search(t.get('url') or '')
            if not mu or t.get('soldout'):
                continue
            if (t.get('date') or '') < today:
                continue
            by_url.setdefault(mu.group(0), []).append((e, t))
    nslots = sum(len(v) for v in by_url.values())
    print('fany_mark_soldout: 対象 %d枠 / 受付ページ %d枚 を読む' % (nslots, len(by_url)))

    marks, parts, unread = [], [], []
    unknown = collections.Counter()
    for i, (u, slots) in enumerate(by_url.items()):
        if i:
            time.sleep(a.sleep)
        page, why = fetch(u)
        items = parse(page) if page else []
        v = judge(items)
        if v is None:
            unread.append((u, slots, why or '券種の状態が見つからない（形が違う）'))
            continue
        for _, s in items:
            if s not in KNOWN:
                unknown[s or '(空)'] += 1
        if v == 'all':
            marks.append((u, slots, items))
        elif v == 'part':
            parts.append((u, slots, items))
        if (i + 1) % 50 == 0:
            print('  …%d/%d枚' % (i + 1, len(by_url)))

    nmark = sum(len(s) for _, s, _ in marks)
    summary = ('全部予定数終了で付ける %d枠（%d枚）/ 一部だけ %d枚 / 読めない %d枚 / '
               '見たことの無い文字 %d種' % (nmark, len(marks), len(parts), len(unread), len(unknown)))
    rep = io.open(REPORT, 'w', encoding='utf-8')
    rep.write('=== fany_mark_soldout (today=%s) apply=%s 対象 %d枠 / %d枚 ===\n\n'
              % (today, a.apply, nslots, len(by_url)))
    rep.write('--- 🔴 全部「予定数終了」＝soldout を付ける ---\n')
    for u, slots, items in marks:
        for e, t in slots:
            rep.write('id%-6s %s｜%s\n' % (e['id'], (e.get('name') or '')[:36], (t.get('type') or '')[:60]))
        rep.write('    %s  %s\n' % (u, ' / '.join('%s=%s' % x for x in items)))
    rep.write('\n--- 🟡 一部だけ予定数終了（触らない）---\n')
    for u, slots, items in parts:
        for e, t in slots:
            rep.write('id%-6s %s｜%s\n' % (e['id'], (e.get('name') or '')[:36], (t.get('type') or '')[:60]))
        rep.write('    %s  %s\n' % (u, ' / '.join('%s=%s' % x for x in items)))
    rep.write('\n--- ⏭️ 読めない（触らない＝確かめられていない）---\n')
    for u, slots, why in unread:
        rep.write('id%s  %s  %s\n' % (','.join(str(e['id']) for e, _ in slots), u, why))
    rep.write('\n--- ❓ 見たことの無い文字 ---\n')
    for s, n in unknown.most_common():
        rep.write('%4d  %s\n' % (n, s))
    rep.write('\n=== %s ===\n' % summary)

    if a.apply and marks:
        take_lock()
        try:
            h = io.open(PATH, encoding='utf-8', newline='').read()   # 鍵を取ってから読み直す
            NL = '\r\n' if '\r\n' in h else '\n'
            m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
            events = json.loads(m.group(2))
            want = {(e['id'], t.get('url'), t.get('type')) for _, s, _ in marks for e, t in s}
            done = 0
            for e in events:
                for t in e.get('tickets') or []:
                    if (e['id'], t.get('url'), t.get('type')) in want and not t.get('soldout'):
                        t['soldout'] = True
                        t['soldoutSince'] = today
                        done += 1
            io.open(PATH, 'w', encoding='utf-8', newline='').write(
                h[:m.start()] + m.group(1)
                + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
                + m.group(3) + h[m.end():])
            raw = open(PATH, 'rb').read()
            rep.write('書いた %d枠 / CRCRLF %d / 素のLF %d （どちらも0が正）\n'
                      % (done, raw.count(b'\r\r\n'), len(re.findall(rb'(?<!\r)\n', raw))))
        finally:
            os.remove(LOCK)
    rep.close()
    print('fany_mark_soldout: %s / apply=%s → %s' % (summary, a.apply, REPORT))
    return 0


def _selftest():
    one = ('<div class="g-sellItems_ticket">\n<p class="g-sellItems_type">\n 前売　一般\n</p>\n'
           '<p class="g-sellItems_state">\n   予定数終了\n  </p>\n'
           '<p class="g-sellItems_price">￥3,000</p>\n</div>')
    old = ('<div class="g-sellItems_ticket"><p class="g-sellItems_name">前売　一般</p>'
           '<p class="g-sellItems_state"> 予定数終了 </p></div>')
    sale = ('<div class="g-sellItems_ticket"><p class="g-sellItems_type">当日</p>'
            '<p class="g-sellItems_state"> 発売中 </p></div>')
    assert parse(one) == [('前売　一般', '予定数終了')], parse(one)
    assert parse(old) == [('前売　一般', '予定数終了')]
    assert judge(parse(one)) == 'all'
    assert judge(parse(one + old)) == 'all'
    assert judge(parse(one + sale)) == 'part'
    assert judge(parse(sale)) == 'none'
    assert judge(parse('<html>混雑しています</html>')) is None
    raw = os.path.join(ROOT, 'tmp', 'x1104', 'spot', 'raw3', '22821_r1.html')
    if os.path.exists(raw):
        it = parse(io.open(raw, encoding='utf-8').read())
        assert judge(it) == 'all', it
        print('  実物 22821_r1.html → %s' % it)
    print('selftest OK: 券種と状態の取り出し（type/name 両方）/ 全部→付ける / 一部→触らない / 読めない→None')
    return 0


if __name__ == '__main__':
    sys.exit(main())
