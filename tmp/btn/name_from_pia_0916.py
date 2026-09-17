# -*- coding: utf-8 -*-
"""ぴあのページを開いて「公演名」だけを取り出す（2026-09-16 夜の検証用）。

検証エージェントが「森山直太朗のエントリに森山良子の武道館が混ざっている」と言ったので、
売り場の中身（状態テキスト）だけでは公演名が分からない＝ページの見出しを読む。

使い方: python tmp/btn/name_from_pia_0916.py <URL> [<URL> ...]
出力は tmp/pia_names_0916.txt（端末の cp932 で日本語が化けるため必ずファイルに書く）
"""
import re
import sys

sys.path.insert(0, 'tools')
from build_pia_entries import fetch  # noqa: E402  sorry.pia 検出つきの fetch


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def main():
    urls = sys.argv[1:]
    lines = []
    for url in urls:
        html = fetch(url)
        if not html:
            lines.append('■ %s\n   （読めなかった）\n' % url)
            continue
        if 'sorry.pia' in html[:2000] or 'アクセスが集中' in html:
            lines.append('■ %s\n   （混雑ページ＝読めなかった）\n' % url)
            continue
        got = []
        m = re.search(r'<title>(.*?)</title>', html, re.S)
        if m:
            got.append('title: ' + strip_tags(m.group(1)))
        for pat in (r'<h1[^>]*>(.*?)</h1>', r'<h2[^>]*>(.*?)</h2>'):
            for mm in re.finditer(pat, html, re.S):
                t = strip_tags(mm.group(1))
                if t and len(t) < 200:
                    got.append('見出し: ' + t)
        # 出演者・公演名のメタ情報
        for mm in re.finditer(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html):
            got.append('og:title: ' + mm.group(1))
        seen, uniq = set(), []
        for g in got:
            if g not in seen:
                seen.add(g)
                uniq.append(g)
        lines.append('■ %s\n%s\n' % (url, '\n'.join('   ' + g for g in uniq[:12])))
    with open('tmp/pia_names_0916.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('wrote tmp/pia_names_0916.txt (%d urls)' % len(urls))


if __name__ == '__main__':
    main()
