# -*- coding: utf-8 -*-
"""pf= が本当に都道府県かを実データで確かめる。
   🚨総数が減っただけでは「効いた」証拠にならない（別の意味で絞られている可能性）。
   返ってきた行の県名を数えて、1県に偏っているかを見る。"""
import io, re, time, urllib.request, collections

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def page(lg, extra, p=1):
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsStatus=0101%s&page=%d" % (lg, extra, p)
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

o = io.open("tmp/probe_pf_0908.txt", "w", encoding="utf-8")
for pf, guess in [("13", "東京のはず"), ("27", "大阪のはず"), ("1", "北海道のはず"), ("40", "福岡のはず")]:
    h = page("01", "&pf=%s" % pf)
    m = re.search(r"全\s*([\d,]+)\s*件中", h)
    total = int(m.group(1).replace(",", "")) if m else -1
    prefs = collections.Counter(re.findall(r"([一-龥ぁ-ん]{2,4}[都道府県])\s*<", h))
    if not prefs:
        prefs = collections.Counter(re.findall(r"（([^（）]{2,4}[都道府県])）", h))
    if not prefs:
        prefs = collections.Counter(re.findall(r">([^<>]{2,4}[都道府県])<", h))
    o.write("pf=%-3s (%s) 総数=%-5s 1ページ目に出た県: %s\n"
            % (pf, guess, total, dict(prefs.most_common(6))))
    time.sleep(2)
o.close()
print("wrote tmp/probe_pf_0908.txt")
