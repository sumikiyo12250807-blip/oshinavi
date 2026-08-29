# -*- coding: utf-8 -*-
"""売り切れ表示のまま残している枠の「飛び先URL」がまだ生きているかを見張る（恒久ツール）。

なぜ要るか（ユーザー指示 2026-08-28）:
  「売り切れでも売り場に見に行けるようにタップでURLで飛べるようにしておいて。
    もし、それがなくなったら乗せるのもやめるようにできる？」
  ＝予定枚数終了・販売終了の枠は消さずに出し続ける方針（feedback_soldout_keep_visible）だが、
    飛び先のページ自体が消えたら「押しても何も無い枠」になる。それは載せる意味がない。

🚨 消していい条件はひとつだけ＝**そのURLが確かに消えている**こと。
   - ぴあ: eventCd/eventBundleCd が無効化されて「該当する公演がありません」等になる、または 404
   - e+  : /sf/detail/ が 404
   混雑ページ（sorry.pia.jp）・429・タイムアウト・接続エラーは **判定しない**（巻き添えで消さない）。
   [[reference_pia_rate_limit_429]] / [[feedback_pia_eventcd_gone]]

使い方:
  python tools/soldout_deadlink_scan.py            # 走査のみ（消さない）
  python tools/soldout_deadlink_scan.py --apply    # DEADと確定した枠だけ落とす
"""
import io
import json
import re
import sys
import time
import datetime
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
TODAY = datetime.date.today().isoformat()

# ページが「もう無い」と言い切れる文言だけを並べる。曖昧なものは入れない。
PIA_GONE = (
    '該当する公演がありません',
    'ご指定の公演は見つかりませんでした',
    'お探しのページは見つかりませんでした',
    'ページが見つかりません',
)
EPLUS_GONE = (
    'お探しのページは見つかりませんでした',
    'ページが見つかりません',
)


def load():
    src = io.open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    assert m, 'EVENTS配列が見つからない'
    return src, m, json.loads(m.group(2))


def fetch(url):
    """(status, text) を返す。status は 'OK' / 'GONE' / 'SKIP'。
    SKIP は混雑・429・通信エラー＝判定しない。"""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl()
            body = r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 'GONE', 'HTTP 404'
        if e.code in (429, 500, 502, 503, 504):
            return 'SKIP', 'HTTP %d' % e.code
        return 'SKIP', 'HTTP %d' % e.code
    except Exception as e:
        return 'SKIP', str(e)[:60]

    if 'sorry.pia.jp' in final:
        return 'SKIP', '混雑ページ'
    words = EPLUS_GONE if 'eplus.jp' in url else PIA_GONE
    for w in words:
        if w in body:
            return 'GONE', w
    return 'OK', ''


def main():
    apply_mode = '--apply' in sys.argv
    src, m, events = load()

    targets = []
    for e in events:
        if (e.get('date') or '') < TODAY:
            continue  # 公演が終わった子は renderCard の安全弁で消える
        for t in (e.get('tickets') or []):
            if not t.get('soldout'):
                continue
            url = t.get('url') or (e.get('links') or {}).get('pia') \
                or (e.get('links') or {}).get('eplus')
            if not url:
                continue
            targets.append((e, t, url))

    print('=== 売り切れ表示の枠の飛び先チェック (today=%s) ===' % TODAY)
    print('  対象 %d枠' % len(targets))

    cache = {}
    dead, skipped, ok = [], [], 0
    for i, (e, t, url) in enumerate(targets, 1):
        if url in cache:
            st, why = cache[url]
        else:
            st, why = fetch(url)
            cache[url] = (st, why)
            time.sleep(1.2)
        if st == 'OK':
            ok += 1
        elif st == 'GONE':
            dead.append((e, t, url, why))
            print('  [%d/%d] 🚨DEAD id=%s %s | %s' % (i, len(targets), e['id'], t.get('type'), why))
        else:
            skipped.append((e, t, url, why))
    print()
    print('=== 生存 %d / 🚨消えた %d / 判定できず %d（混雑・429などは触らない）===' % (
        ok, len(dead), len(skipped)))

    if dead:
        print()
        print('🚨 飛び先が消えている枠（--apply で落とす）:')
        for e, t, url, why in dead:
            print('  id=%-5s %s' % (e['id'], e.get('name')))
            print('        %s' % t.get('type'))
            print('        %s  ← %s' % (url, why))

    if not apply_mode:
        print()
        print('(走査のみ。落とすなら --apply)')
        return 0
    if not dead:
        return 0

    bak = 'index.html.bak_%s_soldoutdead' % datetime.date.today().strftime('%m%d')
    io.open(bak, 'w', encoding='utf-8', newline='').write(src)
    drop = {(e['id'], id(t)) for e, t, _, _ in dead}
    n = 0
    for e in events:
        keep = []
        for t in (e.get('tickets') or []):
            if (e['id'], id(t)) in drop:
                n += 1
                continue
            keep.append(t)
        e['tickets'] = keep
    nl = '\r\n' if '\r\n' in src[:4000] else '\n'
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(
        src[:m.start(2)] + dumped + src[m.end(2):])
    print()
    print('=== %d枠を落とした (backup: %s) ===' % (n, bak))
    return 0


if __name__ == '__main__':
    sys.exit(main())
