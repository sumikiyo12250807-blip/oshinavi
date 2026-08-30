# -*- coding: utf-8 -*-
"""X投稿の機械検品（恒久ツール・2026-08-30 新設。毎回 tmp/xcheck_MMDD.py を書き捨てていたのをやめた）。

memory: feedback_x_post_method_0825 の「検品（機械でやる・目分量禁止）」10項目をそのまま実装。
  ①字数 ②1行目がピックアップ見出しか ③「。」の直後が改行か ④CTA ⑤素のoshinavi.jp
  ⑥二人称 ⑦封印フレーズ ⑧件数表記 ⑨締めが全本違うか ⑩本文の曜日を実カレンダーと照合

使い方:
  python tools/x_check.py tmp/x0831/post*.txt
  python tools/x_check.py --min 380 --max 430 tmp/x0831/post1.txt   # 主役だけ字数を厳しく見る
"""
import argparse
import datetime
import glob
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEAD = re.compile(r'^OSHINAVIの"[^"]+"ピックアップ🎫$')
CTA = "▼チケット情報はこちら"
URL_OK = "oshinavi.jp"
NG_URL = re.compile(r"https?://\s*oshinavi\.jp|oshinavi\.jp/?\?x=")
NG_2ND = ["あなた", "みなさん", "皆さん", "皆様", "みなさま"]
BANNED = ["生で浴び"]                      # memory: feedback_x_phrase_blacklist
NG_REF = ["さっきの", "ひとつ前の投稿", "前の投稿", "先ほどの投稿"]
NG_COUNT = re.compile(r"\d+\s*件(発売|が発売|の発売)")
WD = "月火水木金土日"


def weekday_errors(text, year=2026):
    """本文中の『M/D(曜)』『M月D日(曜)』を実カレンダーと突き合わせる。年跨ぎは1月以降を翌年とみなす。"""
    bad = []
    pats = [re.compile(r"(\d{1,2})/(\d{1,2})\(([月火水木金土日])\)"),
            re.compile(r"(\d{1,2})月(\d{1,2})日\(([月火水木金土日])\)")]
    for p in pats:
        for m, d, w in p.findall(text):
            m, d = int(m), int(d)
            y = year + 1 if m <= 6 else year          # 7〜12月は今年、1〜6月は翌年の公演とみなす
            try:
                real = WD[datetime.date(y, m, d).weekday()]
            except ValueError:
                bad.append("%d/%d は存在しない日付" % (m, d)); continue
            if real != w:
                bad.append("%d/%d(%s) ← 実際は %s (%d年)" % (m, d, w, real, y))
    return bad


def check(path, lo, hi):
    t = open(path, encoding="utf-8").read().rstrip("\n")
    lines = t.split("\n")
    ng = []
    n = len(t.replace("\n", ""))                      # 改行を除いた字数
    if lo and not (lo <= n <= hi):
        ng.append("字数 %d（目安 %d〜%d）" % (n, lo, hi))
    if not HEAD.match(lines[0].strip()):
        ng.append("1行目がピックアップ見出しでない: %r" % lines[0][:40])
    # 「。」の直後が改行か（末尾と閉じ括弧・記号の前は除く）
    for m in re.finditer(r"。(?!$)", t):
        nxt = t[m.end():m.end() + 1]
        if nxt and nxt not in "\n）」』】”":
            ng.append("「。」の直後が改行でない: …%s" % t[max(0, m.start() - 12):m.end() + 8].replace("\n", "⏎"))
            break
    if CTA not in t:
        ng.append("CTA『%s』が無い" % CTA)
    if URL_OK not in t:
        ng.append("oshinavi.jp が無い")
    if NG_URL.search(t):
        ng.append("URLに https:// か ?x= が混ざっている")
    for w in NG_2ND:
        if w in t:
            ng.append("二人称『%s』" % w)
    for w in BANNED:
        if w in t:
            ng.append("🚫封印フレーズ『%s』" % w)
    for w in NG_REF:
        if w in t:
            ng.append("他投稿への参照『%s』（1本ずつ単独で読まれる）" % w)
    if NG_COUNT.search(t):
        ng.append("件数表記『%s』" % NG_COUNT.search(t).group(0))
    ng += ["曜日ズレ " + b for b in weekday_errors(t)]
    tail = [l for l in lines if l.strip() and not l.startswith("#")][-1]
    return n, ng, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--min", type=int, default=0)
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    files = []
    for f in a.files:
        files += sorted(glob.glob(f)) or [f]
    tails, bad = [], 0
    for f in files:
        n, ng, tail = check(f, a.min, a.max)
        tails.append((f, tail))
        print("== %s == %d字" % (f, n))
        if ng:
            bad += 1
            for x in ng:
                print("   ❌ " + x)
        else:
            print("   ✅ 指摘なし")
    print("\n=== 締めの一文（全部ちがうか目で見る） ===")
    seen = {}
    for f, tail in tails:
        dup = " 🚨前と同じ" if tail in seen else ""
        seen[tail] = f
        print("  %s: %s%s" % (f.split("/")[-1], tail[:60], dup))
    print("\n=== %d本中 指摘あり %d本 ===" % (len(files), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
