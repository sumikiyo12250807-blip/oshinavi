# -*- coding: utf-8 -*-
"""2026-08-10 夕：新着44件(id3974-4017)をユーザーOK後にジャンル確定する。
- 原則＝ぴあカテゴリ由来の `_genre` をそのまま `genre` に移す（自分で再分類しない
  ＝[[project_vendor_genre_autoassign]]）。
- 例外4件だけユーザー確認済み：
    4012 渋谷すばる FAN MEETING    engeki → jpop  （主役が歌手。ぴあは会場業態で付けただけ）
    4010 CANNONBALL外伝           engeki → jpop  （ぴあ大分類は音楽・屋内なのでfesにしない）
    3992 ボイスシネマ声優口演ライブ  engeki のまま ＋extraGenres seiyuu
    4007 CNBLUE                  yougaku のまま ＋extraGenres kpop
- 適用後は `_genre`/`_extraGenres`/`_piaSub` を削除し、NEW_ORDER を空にする。
index.html は CRLF を維持（[[feedback_index_html_crlf_preserve]]）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_assign_pm"
OVERRIDE = {4012: "jpop", 4010: "jpop"}
EXTRA_ADD = {3992: ["seiyuu"], 4007: ["kpop"]}

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
    for eid in sorted(extra_done):
        print("  extraGenres id=%d → [%s]" % (eid, ", ".join(extra_done[eid])))
    print("NEW_ORDER を空にした (backup: %s)" % BAK)


main()
