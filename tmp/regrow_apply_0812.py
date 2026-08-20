# -*- coding: utf-8 -*-
"""2026-08-12 朝：reconcile --new のMISSING2エントリをぴあ実データで作り直す。
- 4071 CANDY TUNE … 2次プレリザーブ（香川・高知 11/24〜11/26公演）8/12 11:00発売 を追加。
                    会場もレクザムホール／新来島高知重工重工ホールの2つが増えた。
- 4086 ハラミちゃん … 先行(〜8/11)が終わり、プレリザーブ2枠(〜8/23)に入れ替わった。
根拠＝tools/build_pia_entries.py の機械パース結果 tmp/regrow_built_0812.json。
人が決めた _genre（4071=jpop）は守る（build の推定 engeki で上書きしない）。
"""
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0812_regrow"
KEEP_GENRE = {4071: "jpop"}


def entry_span(src, eid):
    m = re.search(r'\n\s*\{\s*"id": %d,' % eid, src)
    if not m:
        raise SystemExit("id=%d が見つからない" % eid)
    i = src.index("{", m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return i, j + 1


def main():
    built = json.load(open("tmp/regrow_built_0812.json", encoding="utf-8-sig"))
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    for ent in built:
        eid = ent["id"]
        if eid in KEEP_GENRE:
            ent["_genre"] = KEEP_GENRE[eid]
        body = json.dumps(ent, ensure_ascii=False, indent=2)
        # EVENTS配列の中は2スペース字下げ。1行目以外に2スペース足して既存と揃える。
        body = "\n".join([body.split("\n")[0]] + ["  " + ln for ln in body.split("\n")[1:]])
        body = body.replace("\r\n", "\n").replace("\n", "\r\n")
        i, j = entry_span(src, eid)
        src = src[:i] + body + src[j:]
        print("id=%d 置換 %d→%d文字 / 枠%d" % (eid, j - i, len(body), len(ent["tickets"])))
    out = src.encode("utf-8")
    assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
    open(P, "wb").write(out)
    print("書き込み完了 (backup: %s)" % BAK)


main()
