# -*- coding: utf-8 -*-
"""受付中(0101)を1,000未満に割れる軸を実測で探す。
   総数が変われば「効いている」、変わらなければ「無視されている」。
   🚨2桁のrlsStatusが無視された前例があるので、必ず総数で確かめる。"""
import io, re, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
BASE = 4701   # lg=01 受付中0101 の総数（絞り無し）


def total(extra):
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsStatus=0101%s&page=1" % extra
    req = urllib.request.Request(url, headers=UA)
    h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    m = re.search(r"全\s*([\d,]+)\s*件中", h)
    return int(m.group(1).replace(",", "")) if m else -1


TESTS = [
    ("&sg=0101", "sg=0101"), ("&sg=01", "sg=01"),
    ("&rg=01", "rg=01"), ("&rg=0001", "rg=0001"),
    ("&pf=13", "pf=13(東京?)"), ("&pref=13", "pref=13"),
    ("&kw=", "kw=(空)"),
    ("&rlsIn=03", "rlsIn=03"),
    ("&area=01", "area=01"),
]

o = io.open("tmp/probe_split_0908.txt", "w", encoding="utf-8")
o.write("lg=01 受付中0101 の総数（絞り無し）= %d\n\n" % BASE)
o.write("| 足した条件 | 総数 | 効いたか |\n|---|---|---|\n")
for extra, label in TESTS:
    try:
        n = total(extra)
    except Exception as ex:
        o.write("| %s | 取得できず(%s) | ? |\n" % (label, str(ex)[:30]))
        time.sleep(2)
        continue
    o.write("| %s | %s | %s |\n" % (label, n, "効いた" if 0 <= n < BASE else "無視された"))
    time.sleep(2)
o.close()
print("wrote tmp/probe_split_0908.txt")
