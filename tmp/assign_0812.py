# -*- coding: utf-8 -*-
"""2026-08-12 朝：新着49件(id4068-4118)をユーザーOK後にジャンル確定する。
- 原則＝ぴあカテゴリ由来の `_genre` をそのまま `genre` に移す（自分で再分類しない
  ＝[[project_vendor_genre_autoassign]]）。
- ユーザー確認済みの例外1件：
    4075 昭和・平成歌謡ナイト Vol.3 → jpop ＋extraGenres enka（前工程で _genre に反映済み）
- 適用後は `_genre`/`_extraGenres`/`_piaSub` を削除し、NEW_ORDER を空にする。
index.html は CRLF を維持（[[feedback_index_html_crlf_preserve]]）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0812_assign"
OVERRIDE = {}
EXTRA_ADD = {}

BLOCK = re.compile(
    r'(?P<head>"id": (?P<id>\d+),.*?)'
    r'    "genre": "new",\r\n'
    r'    "_genre": "(?P<g>[^"]*)",\r\n'
    r'    "_extraGenres": \[(?P<eg>[^\]]*)\],\r\n'
    r'    "_piaSub": "(?P<sub>[^"]*)",\r\n',
    re.S,
)


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    done = {}
    extra_done = {}

    def rep(m):
        eid = int(m.group("id"))
        g = OVERRIDE.get(eid, m.group("g"))
        assert g and g != "new", "id=%d のジャンルが決まっていない" % eid
        eg = [x.strip() for x in m.group("eg").split(",") if x.strip()]
        for add in EXTRA_ADD.get(eid, []):
            q = '"%s"' % add
            if q not in eg:
                eg.append(q)
        out = m.group("head") + '    "genre": "%s",\r\n' % g
        if eg:
            out += '    "extraGenres": [%s],\r\n' % ", ".join(eg)
            extra_done[eid] = eg
        done[eid] = g
        return out

    src2, n = BLOCK.subn(rep, src)
    print("振り分け %d件" % n)

    src2, k = re.subn(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]", r"\g<1>[]", src2, count=1)
    assert k == 1, "NEW_ORDER が見つからない"

    assert '"genre": "new"' not in src2, "genre:new が残っている"
    assert '"_genre"' not in src2, "_genre が残っている"
    assert '"_piaSub"' not in src2, "_piaSub が残っている"

    out = src2.encode("utf-8")
    assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
    open(P, "wb").write(out)

    import collections
    print("内訳:", dict(collections.Counter(done.values())))
    for eid in sorted(extra_done):
        print("  extraGenres id=%d → [%s]" % (eid, ", ".join(extra_done[eid])))
    print("NEW_ORDER を空にした (backup: %s)" % BAK)


main()
