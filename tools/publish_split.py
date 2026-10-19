# -*- coding: utf-8 -*-
"""公開用に index.html の EVENTS を別ファイルへ切り出す（2026-10-13・ユーザー「①合ってる　お願いします」）

Why: index.html が 29MB あり、Googlebot は1ファイル15MBまでしか読まない。
     途中で切られた EVENTS の <script> は構文エラーになり、head で付けた .js のせいで
     SSR一覧も隠れる＝Google には「空のページ」に見えていた。
     EVENTS を 4MB 前後の ev/*.js に分けて読み込めば、HTML は約7MB・各ファイルも15MB未満になる。

作業用の index.html（道具が読み書きする方）は変えない。Netlify のビルド（netlify.toml）で
公開の直前に、ビルド用の複製の中だけを書き換える。

使い方:
  python tools/publish_split.py --inplace          # Netlify のビルドで（その場で書き換え）
  python tools/publish_split.py --out <dir>        # 手元で試す（<dir>/index.html と <dir>/ev/ を作る）
"""
import argparse, datetime, hashlib, io, json, os, re, sys

CHUNK = 4_000_000  # 1ファイルの目安（バイト）
HEAD_DAYS = 7      # 先に読む分＝今日から7日以内に発売・締切が来る枠を持つカード（画面の上に並ぶ分）
DEAD_DAYS = 3      # 締切がこれより前に過ぎた枠は配らない（画面には出ない枠）


def slim(E, page, today):
    """🆕2026-10-19 ユーザー「うん　お願いします」＝iPhone で他のアプリを開いていると30秒以上かかる対策の②。
    画面で使わない欄（ページのプログラムに名前が出てこない「_」始まりの欄・verifiedAt）と、
    締切が DEAD_DAYS 日より前に過ぎた枠（売り切れ・予定枚数まで販売の印が無いもの＝画面に出ない）を、配る分からだけ外す。
    作業用の index.html は変えない。"""
    cut = (today - datetime.timedelta(days=DEAD_DAYS)).isoformat()
    used = set(re.findall(r'\b(_\w+)\b', page))
    keys = drop_t = 0
    for e in E:
        for kk in [kk for kk in e if (kk.startswith('_') and kk not in used) or (kk == 'verifiedAt' and 'verifiedAt' not in page)]:
            del e[kk]; keys += 1
        ts = e.get('tickets')
        if ts:
            keep = [x for x in ts if x.get('soldout') or x.get('saleUntilSoldOut') or (x.get('date') or '9999') >= cut]
            drop_t += len(ts) - len(keep)
            e['tickets'] = keep
    return keys, drop_t


def is_head(e, today):
    """画面の並び（日付が早い順）の上に来うるカード＝発売日か締切が今日〜HEAD_DAYS 日の枠を1つでも持つ／新着プール"""
    if e.get('genre') == 'new':
        return True
    lo = (today - datetime.timedelta(days=1)).isoformat()
    hi = (today + datetime.timedelta(days=HEAD_DAYS)).isoformat()
    for x in e.get('tickets') or []:
        if x.get('soldout'):
            continue
        sd, d = x.get('startDate') or '', x.get('date') or ''
        if (sd and lo <= sd <= hi) or (d and lo <= d <= hi):
            return True
    return False


def chunks(rows):
    parts, cur, size = [], [], 0
    for x in rows:
        if cur and size + len(x.encode('utf-8')) > CHUNK:
            parts.append(cur); cur, size = [], 0
        cur.append(x); size += len(x.encode('utf-8')) + 1
    if cur:
        parts.append(cur)
    return parts


def split(src, today=None):
    key = 'const EVENTS = '
    i = src.index(key)
    j = i + len(key)
    E, end = json.JSONDecoder().raw_decode(src, j)
    k = end
    if src[k:k + 1] == ';':
        k += 1
    # EVENTS を含む <script> の開始位置
    t = src.rfind('<script>', 0, i)
    assert t != -1 and '</script>' not in src[t:i], 'EVENTS の <script> が見つからない'
    n0 = len(E)
    today = today or (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()
    keys, drop_t = slim(E, src[:i] + src[k:], today)
    if '__OSHI_REST' in src[:i] + src[k:]:   # ページ側に後読み（loadRest）がある時だけ分ける
        head = [e for e in E if is_head(e, today)]
        rest = [e for e in E if not is_head(e, today)]
    else:
        head, rest = E, []
    dump = lambda e: json.dumps(e, ensure_ascii=False, separators=(',', ':'))
    h = hashlib.sha1(src[j:end].encode('utf-8')).hexdigest()[:10]
    files, sync, lazy = {}, [], []
    for tag, rows, bucket in (('h', head, sync), ('r', rest, lazy)):
        for n, p in enumerate(chunks([dump(e) for e in rows]), 1):
            f = f'ev/events-{h}-{tag}{n}.js'
            files[f] = 'Array.prototype.push.apply(window.__OSHI_EV=window.__OSHI_EV||[],[\n' + ',\n'.join(p) + '\n]);\n'
            bucket.append(f)
    # 先に出す分だけを同期で読み、残りは window.__OSHI_REST に並べてページ側（loadRest）が描いたあとで読む
    tags = ''.join(f'<script src="{f}"></script>\n' for f in sync)
    tags += '<script>window.__OSHI_REST=' + json.dumps(lazy) + ';</script>\n'
    out = src[:t] + tags + src[t:i] + 'const EVENTS = window.__OSHI_EV || [];' + src[k:]
    assert len(head) + len(rest) == n0
    print(f'配る分を削った：使わない欄 {keys}個・締切が{DEAD_DAYS}日より前に過ぎた枠 {drop_t}枠／先に読む {len(head)}件・後で読む {len(rest)}件')
    return out, files, n0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inplace', action='store_true')
    ap.add_argument('--out')
    ap.add_argument('--root', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    a = ap.parse_args()
    if not a.inplace and not a.out:
        ap.error('--inplace か --out を付ける')
    root = os.path.abspath(a.root)
    src = io.open(os.path.join(root, 'index.html'), encoding='utf-8', newline='').read()
    if 'window.__OSHI_EV' in src:
        print('切り出し済み＝何もしない'); return
    out, files, n = split(src)
    dst = root if a.inplace else os.path.abspath(a.out)
    os.makedirs(os.path.join(dst, 'ev'), exist_ok=True)
    for f, body in files.items():
        io.open(os.path.join(dst, f), 'w', encoding='utf-8', newline='\n').write(body)
    io.open(os.path.join(dst, 'index.html'), 'w', encoding='utf-8', newline='').write(out)
    mb = lambda s: round(len(s.encode('utf-8')) / 1e6, 2)
    print(f'EVENTS {n}件 → {len(files)}ファイル（{", ".join(str(mb(b)) + "MB" for b in files.values())}）／index.html {mb(src)}MB → {mb(out)}MB')
    if mb(out) >= 15 or any(mb(b) >= 15 for b in files.values()):
        print('🚨 15MBを超えるファイルがある'); sys.exit(1)


if __name__ == '__main__':
    main()
