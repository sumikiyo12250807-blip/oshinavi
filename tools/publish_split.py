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
import argparse, hashlib, io, json, os, sys

CHUNK = 4_000_000  # 1ファイルの目安（バイト）


def split(src):
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
    parts, cur, size = [], [], 0
    for e in E:
        x = json.dumps(e, ensure_ascii=False, separators=(',', ':'))
        if cur and size + len(x.encode('utf-8')) > CHUNK:
            parts.append(cur); cur, size = [], 0
        cur.append(x); size += len(x.encode('utf-8')) + 1
    if cur:
        parts.append(cur)
    h = hashlib.sha1(src[j:end].encode('utf-8')).hexdigest()[:10]
    files = {}
    for n, p in enumerate(parts, 1):
        files[f'ev/events-{h}-{n}.js'] = 'Array.prototype.push.apply(window.__OSHI_EV=window.__OSHI_EV||[],[\n' + ',\n'.join(p) + '\n]);\n'
    tags = ''.join(f'<script src="{f}"></script>\n' for f in files)
    out = src[:t] + tags + src[t:i] + 'const EVENTS = window.__OSHI_EV || [];' + src[k:]
    assert sum(len(p) for p in parts) == len(E)
    return out, files, len(E)


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
