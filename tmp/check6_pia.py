# -*- coding: utf-8 -*-
import re, time, io, sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

targets = [
    (1782, "https://t.pia.jp/pia/event/event.do?eventCd=2623994"),
    (2072, "https://t.pia.jp/pia/event/event.do?eventCd=2625053"),
    (2359, "https://t.pia.jp/pia/event/event.do?eventCd=2626351"),
    (2630, "https://t.pia.jp/pia/event/event.do?eventCd=2624590"),
    (2631, "https://t.pia.jp/pia/event/event.do?eventCd=2624617"),
]

out = io.open(r"C:\Users\user\oshinavi\tmp\check6_pia_out.txt", "w", encoding="utf-8")

def strip(h):
    h = re.sub(r"<[^>]+>", " ", h)
    h = re.sub(r"\s+", " ", h)
    return h.strip()

for i, (eid, url) in enumerate(targets):
    if i:
        time.sleep(6)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    try:
        raw = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
    except Exception as ex:
        out.write("=== id=%s %s\nERROR %r\n\n" % (eid, url, ex))
        continue
    io.open(r"C:\Users\user\oshinavi\tmp\pia_%s.html" % eid, "w", encoding="utf-8").write(raw)
    out.write("=== id=%s %s\n" % (eid, url))
    out.write("len=%d\n" % len(raw))
    out.write("sorry_page=%s notfound=%s\n" % (
        ("sorry" in raw.lower() and "混雑" in raw),
        ("見つかりませんでした" in raw),
    ))
    ttl = re.search(r"<title>(.*?)</title>", raw, re.S)
    out.write("title=%s\n" % (strip(ttl.group(1)) if ttl else "?"))
    # ticket item blocks
    items = re.findall(r'<li class="ticket-item.*?</li>', raw, re.S)
    if not items:
        items = re.findall(r'class="ticket-item__inner".{0,4000?}', raw, re.S)
    out.write("item_blocks=%d\n" % len(items))
    for it in items:
        name = re.search(r'ticket-item__name[^>]*>(.*?)</', it, re.S)
        st = re.search(r'ticket-item__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        per = re.findall(r'\d{4}/\d{1,2}/\d{1,2}[^<]*', strip(it))
        out.write("  - name=%s | status=%s/%s | dates=%s\n" % (
            strip(name.group(1)) if name else "?",
            st.group(1) if st else "?",
            strip(st.group(2)) if st else "?",
            " ; ".join(per[:6]),
        ))
    # fallback: all status texts
    sts = re.findall(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', raw, re.S)
    out.write("all_status=%s\n" % [(a, strip(b)) for a, b in sts])
    # any date-like strings near 販売
    out.write("has_haibaisyuryo=%s has_uketsuke_chu=%s has_yoteimaisu=%s\n" % (
        "販売終了" in raw, "受付中" in raw, "予定枚数終了" in raw))
    out.write("has_haishin=%s archive=%s\n" % ("配信" in raw, "アーカイブ" in raw))
    out.write("\n")

out.close()
print("done")
