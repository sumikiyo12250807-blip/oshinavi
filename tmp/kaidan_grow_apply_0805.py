# -*- coding: utf-8 -*-
"""怪談スイープの仕上げ。

  ① id44 稲川淳二 … 長野1公演(e+枠)だけだったのを、ぴあbundleの【17枠・全国ツアー】に育てる。
       - name から「(長野公演)」を外す（全国ツアーになるので嘘になる）
       - venue は会場27個の羅列をやめて「全国ツアー」に（id21 ORANGE RANGE 等と同じ流儀）
       - 既存のe+長野枠は、ぴあ側に長野公演(10/12〜10/17)があるので落とす＝二重表示を防ぐ
         （購入先の優先はぴあ＝[[feedback_vendor_priority]]／今朝のヒール修正と同じ考え方）
       - links.eplus は残す（売り場としては生きている）
  ② tmp/kaidan_grow_built.json の id3804 配信版の下書きジャンルを kaidan に直す

index.html は newline='' で読み書きしてCRLFを保つ（[[feedback_index_html_crlf_preserve]]）。
"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")
BAK = os.path.join(ROOT, "index.html.bak_0805_inagawa")

# ---- ② 配信版の下書きジャンル ----
GP = os.path.join(ROOT, "tmp", "kaidan_grow_built.json")
built = json.load(io.open(GP, encoding="utf-8-sig"))
for e in built:
    if e["id"] == 3804:
        e["_genre"] = "kaidan"
        e["_extraGenres"] = []
json.dump(built, io.open(GP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("id3804 _genre → kaidan")

new44 = next(e for e in built if e["id"] == 44)

# ---- ① id44 を育てる ----
h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

cur = next(e for e in EVENTS if e["id"] == 44)
print("\n【変更前】id44")
print("   name  :", cur.get("name"))
print("   枠    :", len(cur.get("tickets", [])), "枠 ／ pref", cur.get("prefecture"))
print("   links :", {k: v for k, v in (cur.get("links") or {}).items() if v})

cur["name"] = "MYSTERY NIGHT TOUR 2026 稲川淳二の怪談ナイト"
cur["tickets"] = new44["tickets"]
cur["date"] = new44["date"]
cur["dateLabel"] = "2026年8月11日(火)〜2026年11月15日(日) 全国ツアー"
cur["venue"] = "全国ツアー"
cur["prefecture"] = "全国"
cur.setdefault("links", {})
cur["links"]["pia"] = new44["links"]["pia"]
cur["verifiedAt"] = "2026-08-05"

print("\n【変更後】id44")
print("   name  :", cur["name"])
print("   枠    :", len(cur["tickets"]), "枠 ／ pref", cur["prefecture"])
print("   links :", {k: v for k, v in cur["links"].items() if v})

shutil.copyfile(IDX, BAK)
body = json.dumps(EVENTS, ensure_ascii=False, indent=2)
body = NL.join(body.split("\n"))
h2 = h[:m.start(2)] + body + h[m.end(2):]
io.open(IDX, "w", encoding="utf-8", newline="").write(h2)
print("\n✅ 書き戻し完了（backup: %s）" % os.path.basename(BAK))
