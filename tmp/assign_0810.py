# -*- coding: utf-8 -*-
"""2026-08-10：新着44件(id3927-3973)をユーザーOK後にジャンル確定する。
- 原則＝ぴあカテゴリ由来の `_genre` をそのまま `genre` に移す（自分で再分類しない
  ＝[[project_vendor_genre_autoassign]]）。
- 例外3件だけユーザー確認済み：
    3953 国立劇場 10月声明公演        enka → dento （声明は仏教声楽で演歌ではない）
    3960 モノボケアイドルGP           fes  → idol  （東京カルチャーカルチャー＝屋内・[[feedback_fes_definition]]）
    3962 ギターのガラ・コンサート      fes  → classic（川口リリア＝屋内ホール）
- 適用後は `_genre`/`_extraGenres`/`_piaSub` を削除し、NEW_ORDER を空にする。
index.html は CRLF を維持（[[feedback_index_html_crlf_preserve]]）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_assign"
OVERRIDE = {3953: "dento", 3960: "idol", 3962: "classic"}

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

    def rep(m):
        eid = int(m.group("id"))
        g = OVERRIDE.get(eid, m.group("g"))
        assert g and g != "new", "id=%d のジャンルが決まっていない" % eid
        eg = m.group("eg").strip()
        out = m.group("head") + '    "genre": "%s",\r\n' % g
        if eg:
            out += '    "extraGenres": [%s],\r\n' % eg
        done[eid] = g
        return out

    src2, n = BLOCK.subn(rep, src)
    print("振り分け %d件" % n)

    # NEW_ORDER を空にする（新着タブを0件に）
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
    for eid in sorted(OVERRIDE):
        print("  例外適用 id=%d → %s" % (eid, done.get(eid)))
    print("NEW_ORDER を空にした (backup: %s)" % BAK)


main()
