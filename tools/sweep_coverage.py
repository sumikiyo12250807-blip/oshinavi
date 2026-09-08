# -*- coding: utf-8 -*-
"""都道府県で割ったスイープの「取りこぼし」を数字で確かめる。

🚨 割って回すと、各県のページ到達率が良くても
   「その県を丸ごと飛ばした」ことに気づけない（混雑ページを0件と誤読する型）。
   だから **県ごとの total の合計** と **ジャンル全体の total** を突き合わせる。
   合わなければ、その差が取りこぼし。

使い方: python tools/sweep_coverage.py tmp/sweep0101_0908/_driver.log
"""
import io, re, sys, time, urllib.request, collections

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
GJP = {"01": "音楽", "02": "演劇", "03": "スポーツ", "04": "映画",
       "05": "アート", "06": "イベント", "07": "クラシック"}


def total_of(lg, extra=""):
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsStatus=0101%s&page=1" % (lg, extra)
    try:
        req = urllib.request.Request(url, headers=UA)
        h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return None                      # 取得できなかった＝0件ではない
    if "sorry" in h[:2000].lower() or "混雑" in h[:4000]:
        return None                      # 混雑ページ＝0件ではない
    m = re.search(r"全\s*([\d,]+)\s*件中", h)
    if m:
        return int(m.group(1).replace(",", ""))
    # 「該当する情報はありません」等＝本当に0件
    return 0


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "tmp/sweep0101_0908/_driver.log"
    log = io.open(path, encoding="utf-8").read()

    genre_total = {m.group(1): int(m.group(2))
                   for m in re.finditer(r"lg=(\d\d) \([^)]*\) 受付中0101 総数=(\d+)", log)}
    ran = collections.defaultdict(dict)
    for m in re.finditer(r"\[(\d\d)_(?:pf(\d\d)|all)\] rc=\d+ [\d.]+s total=(\d+) pages=(\d+)", log):
        lg, pf, tot, pages = m.group(1), m.group(2) or "all", int(m.group(3)), int(m.group(4))
        ran[lg][pf] = (tot, pages)
    skipped = collections.defaultdict(list)
    cur = None
    for line in log.splitlines():
        g = re.match(r"=== lg=(\d\d)", line)
        if g:
            cur = g.group(1)
        s = re.match(r"\s+pf=(\d\d) 0件", line)
        if s and cur:
            skipped[cur].append(s.group(1))

    o = io.open("tmp/sweep_coverage.txt", "w", encoding="utf-8")
    o.write("# 受付中スイープの取りこぼし点検\n\n")
    o.write("| ジャンル | 全体の総数 | 回した県の合計 | 差 | 飛ばした県 |\n|---|---|---|---|---|\n")
    recheck = []
    for lg in sorted(genre_total):
        gt = genre_total[lg]
        s = sum(v[0] for v in ran.get(lg, {}).values())
        o.write("| %s | %d | %d | **%+d** | %d県 |\n"
                % (GJP.get(lg, lg), gt, s, s - gt, len(skipped.get(lg, []))))
        for pf in skipped.get(lg, []):
            recheck.append((lg, pf))

    o.write("\n## 「0件」と判断して飛ばした県を、もう一度だけ確かめる\n")
    o.write("（混雑ページを0件と誤読していたら、ここで数字が出る）\n\n")
    bad = 0
    for lg, pf in recheck:
        t = total_of(lg, "&pf=%s" % pf)
        if t is None:
            o.write("  🚨 %s pf=%s … 取得できなかった（0件とは限らない）\n" % (GJP.get(lg, lg), pf))
            bad += 1
        elif t > 0:
            o.write("  🚨 %s pf=%s … **%d件あった**＝取りこぼし\n" % (GJP.get(lg, lg), pf, t))
            bad += 1
        time.sleep(1.2)
    if not bad:
        o.write("  ✅ 飛ばした県は全部ほんとうに0件だった。\n")
    o.write("\n再確認した県 %d／要対応 %d\n" % (len(recheck), bad))
    o.close()
    print("wrote tmp/sweep_coverage.txt  genres=%d recheck=%d bad=%d"
          % (len(genre_total), len(recheck), bad))


if __name__ == "__main__":
    main()
