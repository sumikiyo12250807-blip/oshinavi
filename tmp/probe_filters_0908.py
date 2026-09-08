# -*- coding: utf-8 -*-
"""ぴあ rlsInfo.do の絞り込みパラメータ（sg/rg など）を実ページから拾う。
   受付中(0101)は件数が1,000の頭打ちを超えるので、割るための軸を知りたい。"""
import io, re, time, urllib.request, html, collections

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

out = io.open("tmp/probe_filters_0908.txt", "w", encoding="utf-8")
for lg, jp in [("01", "音楽"), ("07", "クラシック"), ("02", "演劇"), ("06", "イベント"), ("03", "スポーツ")]:
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsStatus=0101&page=1" % lg
    try:
        h = get(url)
    except Exception as ex:
        out.write("lg=%s(%s) 取得できず: %s\n" % (lg, jp, ex))
        continue
    m = re.search(r"全\s*([\d,]+)\s*件中", h)
    total = int(m.group(1).replace(",", "")) if m else -1
    out.write("\n=== lg=%s (%s) 受付中0101 総数=%s ===\n" % (lg, jp, total))

    # rlsInfo.do への内部リンクから使われているパラメータ名を集める
    params = collections.Counter()
    for a in re.findall(r'rlsInfo\.do\?([^"\'&>]*(?:&[^"\'>]*)*)', h):
        for kv in html.unescape(a).split("&"):
            if "=" in kv:
                params[kv.split("=")[0]] += 1
    out.write("使われているパラメータ: %s\n" % dict(params))

    # sg= と rg= の実際の値＋その見出し文字
    for key in ("sg", "rg"):
        vals = collections.OrderedDict()
        for m2 in re.finditer(r'rlsInfo\.do\?[^"\']*?\b%s=([\w]+)[^"\']*"[^>]*>([^<]{1,24})' % key, h):
            vals.setdefault(m2.group(1), m2.group(2).strip())
        if vals:
            out.write("  %s の値 %d個:\n" % (key, len(vals)))
            for k, v in vals.items():
                out.write("     %s = %s\n" % (k, v))
        else:
            out.write("  %s の値: 見つからない\n" % key)
    time.sleep(2)
out.close()
print("wrote tmp/probe_filters_0908.txt")
