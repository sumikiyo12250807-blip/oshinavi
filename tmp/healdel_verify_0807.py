# -*- coding: utf-8 -*-
"""昼ヒール削除候補の e+ 個別裏取り（2026-08-07）。
  3876 平成中村座 十月大歌舞伎＝興行トップから公演日一覧、代表2公演の券種ステータス
  3319 関根勤（博品館劇場）＝〜9/25 の枠が本当に生きているか
"""
import html
import io
import re
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def get(u):
    return urllib.request.urlopen(
        urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def blocks(u, label):
    h = get(u)
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    print("  " + label)
    print("   " + u)
    print("   title: " + (clean(m.group(1))[:120] if m else "?"))
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        print("    ・%s → %s" % (head[:140], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
    return h


print("### 3876 平成中村座 十月大歌舞伎 興行トップ")
h = get("https://eplus.jp/sf/detail/0649000001")
m = re.search(r"<title>(.*?)</title>", h, re.S)
print("title: " + (clean(m.group(1))[:120] if m else "?"))
days = [clean(o) for o in re.findall(r"<option[^>]*>(.*?)</option>", h, re.S)]
days = [d for d in days if re.search(r"\d{4}/\d", d)]
print("公演日option %d件:" % len(days))
for d in days:
    print("   " + d)

time.sleep(5)
print("\n### 3876 代表2公演の券種")
blocks("https://eplus.jp/sf/detail/0649000001-P0030031P021003", "1つ目")
time.sleep(5)
blocks("https://eplus.jp/sf/detail/0649000001-P0030031P021032", "2つ目")

time.sleep(5)
print("\n### 3319 関根勤（博品館劇場）〜9/25 の枠")
blocks("https://eplus.jp/sf/detail/3902060001-P0030006P021002", "P021002")
