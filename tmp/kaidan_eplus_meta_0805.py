# -*- coding: utf-8 -*-
"""e+で生きていた怪談公演の会場・県・日時・券種をJSON-LD等から取る（登録用の材料）。"""
import io
import json
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
UA = {"User-Agent": "Mozilla/5.0"}

URLS = [
    ("HORROR TELLER FESTIVAL 2026", "https://eplus.jp/sf/detail/3608720001-P0030004P021001"),
    ("島田秀平×城谷歩×響洋平 彩恐酔夜vol.2", "https://eplus.jp/sf/detail/4544090001-P0030001P021001"),
    ("オカルト超会議 8/21 1部", "https://eplus.jp/sf/detail/4199660003-P0030003P021001"),
    ("オカルト超会議 8/22 1部", "https://eplus.jp/sf/detail/4199660003-P0030003P021002"),
    ("オカルト超会議 8/21 2部", "https://eplus.jp/sf/detail/4199660003-P0030003P021003"),
    ("オカルト超会議 8/22 2部", "https://eplus.jp/sf/detail/4199660003-P0030003P021004"),
    ("怪談五人羽織 2026(e+)", "https://eplus.jp/sf/detail/3917550001-P0030010P021001"),
]

for label, u in URLS:
    h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "replace")
    print("=" * 76)
    print(label)
    print("  ", u)
    # JSON-LD
    for m in re.finditer(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        for o in (d if isinstance(d, list) else [d]):
            if not isinstance(o, dict) or o.get("@type") not in ("Event", "MusicEvent", "TheaterEvent"):
                continue
            loc = o.get("location") or {}
            addr = loc.get("address")
            if isinstance(addr, dict):
                addr = " ".join(str(v) for v in addr.values())
            print("   name  :", o.get("name"))
            print("   start :", o.get("startDate"), "／ end", o.get("endDate"))
            print("   venue :", loc.get("name"), "／", addr)
    # 会場のテキスト表記も拾う
    for pat in (r"会場[^<]{0,4}</[^>]+>\s*<[^>]+>([^<]{2,60})", r'"venue_name"\s*:\s*"([^"]{2,60})"'):
        v = re.findall(pat, h)
        if v:
            print("   会場候補:", " / ".join(dict.fromkeys(v))[:160])
            break
    time.sleep(2)
