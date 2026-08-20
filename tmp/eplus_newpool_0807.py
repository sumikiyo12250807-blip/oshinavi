# -*- coding: utf-8 -*-
"""新着50件（id3877-3926）を e+ で引き直して「ぴあに無い枠」を探す（2026-08-07）。

手順：①artist名でe+検索（ヒット0なら短縮語で再検索）②登録の会場名/公演日と突き合わせて
同じ公演らしい行を候補に出す。③候補は別スクリプトで /sf/detail/ を開いて券種ステータスを読む
（一覧の「一般発売」は券種名であって販売中ではない＝feedback_delete_nonpia_blindspot）。
"""
import io
import json
import re
import subprocess
import sys
import time
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

evs = json.load(open(r"C:\Users\user\oshinavi\tmp\built_0807.json", encoding="utf-8"))


def short(s):
    """検索語を作る＝記号や副題を落として本体だけにする。"""
    s = re.sub(r"[「」『』【】〈〉《》\"'’”“]", " ", s)
    s = re.split(r"[～~]", s)[0]
    s = re.sub(r"\s*(20\d\d[-–]20\d\d|20\d\d)\s*$", "", s.strip())
    return s.strip()


def norm(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[\s　・,，.。/／\-–—~〜～!！?？&＆'\"’”（）()\[\]【】]", "", s)


def search(kw):
    r = subprocess.run([sys.executable, "tmp/eplus_search2_0803.py", kw], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    rows = []
    for ln in txt.splitlines():
        p = [x.strip() for x in ln.split(" | ")]
        # 公演日(koenbi)は空で出ることが多い。行の判定はURLが末尾にあるかで見る。
        if len(p) >= 7 and p[-1].startswith("https://eplus.jp/sf/detail/"):
            rows.append({"koenbi": p[0], "sub": p[1], "venue": p[2], "pref": p[3],
                         "status": p[4], "end": p[5].replace("受付〜", ""), "url": p[-1]})
    return rows


out = []
for n, e in enumerate(evs):
    art = e.get("artist") or ""
    kws = [art]
    s = short(art)
    if s and s != art:
        kws.append(s)
    rows, used = [], ""
    for kw in kws:
        if n or kw != kws[0]:
            time.sleep(3)
        rows = search(kw)
        used = kw
        if rows:
            break
    # 登録の公演日レンジ
    dates = [e.get("date", "")]
    for t in e.get("tickets") or []:
        m = re.search(r"（[^）]*?(\d{1,2})/(\d{1,2})", t.get("type") or "")
    dmax = (e.get("date") or "").replace("-", "")
    vkey = norm(e.get("venue") or "")
    akey = norm(art)
    hits = []
    for r in rows:
        # 会場名／公演日／興行名のどれかが登録と噛み合う行を候補にする。
        vn = norm(r["venue"])
        same_venue = bool(vn) and len(vn) >= 4 and (vn[:10] in vkey or vkey[:10] in vn)
        same_date = bool(r["koenbi"]) and "20260807" <= r["koenbi"] <= dmax
        same_sub = bool(norm(r["sub"])) and len(norm(r["sub"])) >= 5 and norm(r["sub"])[:8] in akey
        if same_venue or same_date or same_sub:
            hits.append(r)
    # 何も噛み合わないがヒット自体が少ない時は全部見せる（判定材料を捨てない）
    if not hits and 0 < len(rows) <= 6:
        hits = rows[:]
    out.append({"id": e["id"], "artist": art, "kw": used, "date": e.get("date"),
                "venue": e.get("venue"), "pref": e.get("prefecture"),
                "n_all": len(rows), "hits": hits})
    print("id%-5d %-34s 検索語「%s」 e+全%d件 / 噛み合う%d件" %
          (e["id"], art[:34], used[:24], len(rows), len(hits)))

json.dump(out, open("tmp/eplus_newpool_0807.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n→ tmp/eplus_newpool_0807.json")
