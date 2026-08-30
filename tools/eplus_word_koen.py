# -*- coding: utf-8 -*-
"""e+ のアーティスト（wordID）に紐づく**全公演**を公開APIから取る。

🚨🚨 なぜ要るか（2026-08-30・ユーザーが画面で発見 → エージェント2本が原因を特定）
  - `/sf/detail/` の JSON-LD は **多公演ツアーでも一部の公演しか持たない**
  - `/sf/word/` のHTMLは **先頭5公演しか出さない**（残りは「もっと見る」でJS）
  → この2つだけで作ると **ツアーの大半が落ちる**。実測＝黒蜜15公演中2件・ビバラッシュ15公演中2件しか
    登録できていなかった（35件中12件・約50公演の取りこぼし）。

## API（e+ 自身が「もっと見る」で叩いているもの）
```
https://api.eplus.jp/v3/koen?word_id_list=<10桁wordID>&kogyo_word_himozuke_flag=<0|1>
   &sort_key=koenbi&shutoku_kensu=200&shutoku_start_ichi=<1,201,...>
ヘッダ: X-APIToken: FGXySj3mTd
```
- レスポンスは `data.record_list`（`so_kensu` が総件数）
- `shutoku_kensu` は **200が上限**（256は400エラー）
- 🚨`kogyo_word_himozuke_flag` は **0と1で結果が違う**（1=興行紐づけ／0=公演紐づけ）。
  **両方引いて union しないと落ちる**（TOKIWA FESは1では出ない／黒蜜は0だけだと欠ける）
- `uketsuke_status`＝ 0:受付中 / 1:予定枚数終了 / 2,3:受付前 / 4,5:受付終了
- ⚠️アーティストページには「男性ダンスボーカルグループ」のような**ジャンル語のwordID**が混ざる。
  名寄せに使うとゴミが入るので、**公演ページから拾った wordID だけ**を使う。

使い方:
  python tools/eplus_word_koen.py 0000022177            # そのwordIDの全公演
  python tools/eplus_word_koen.py --from-url https://eplus.jp/sf/detail/4588510001-P0030001P021001
"""
import argparse
import json
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
TOKEN = "FGXySj3mTd"


def _get(url, sleep=0.6):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja",
                                               "X-APIToken": TOKEN})
    with urllib.request.urlopen(req, timeout=40) as r:
        t = r.read().decode("utf-8", "replace")
    time.sleep(sleep)
    return t


def koen_by_word(wid, sleep=0.6):
    """wordID の全公演レコードを返す（flag 0/1 の union・ページング対応）。"""
    seen, out = set(), []
    for flag in (1, 0):
        start = 1
        while True:
            u = ("https://api.eplus.jp/v3/koen?word_id_list=%s&kogyo_word_himozuke_flag=%d"
                 "&sort_key=koenbi&shutoku_kensu=200&shutoku_start_ichi=%d" % (wid, flag, start))
            try:
                d = json.loads(_get(u, sleep))["data"]
            except Exception as e:
                print("  ! API失敗 flag=%d start=%d %s" % (flag, start, str(e)[:60]))
                break
            recs = d.get("record_list") or []
            for r in recs:
                k = (r.get("kogyo_code"), r.get("kogyo_sub_code"), r.get("koen_code"))
                if k in seen:
                    continue
                seen.add(k)
                out.append(r)
            tot = d.get("so_kensu") or 0
            start += len(recs)
            if not recs or start > tot:
                break
    return out


def simp(r):
    ks = r.get("kanren_kogyo_sub") or {}
    nm = (ks.get("kogyo_name_1") or "")
    if ks.get("kogyo_name_2"):
        nm += " " + ks["kogyo_name_2"]
    v = r.get("kanren_venue") or {}
    return {
        "date": r.get("koenbi_term"),
        "open": r.get("kaijo_time"),
        "start": r.get("kaien_time"),
        "name": nm.strip(),
        "venue": v.get("venue_name"),
        "pref": v.get("todofuken_name"),
        "url": r.get("koen_detail_url_pc"),
        "status": r.get("uketsuke_status"),
    }


def word_id_from_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=40) as r:
        h = r.read().decode("utf-8", "replace")
    m = re.search(r"/sf/word/(\d+)", h)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("word_id", nargs="?", default="")
    ap.add_argument("--from-url", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    wid = a.word_id
    if not wid and a.from_url:
        wid = word_id_from_page(a.from_url)
        print("公演ページから wordID を取った: %s" % wid)
    if not wid:
        print("wordID か --from-url が要る"); return 2

    recs = [simp(r) for r in koen_by_word(wid)]
    recs.sort(key=lambda x: (x["date"] or "", x["start"] or ""))
    print("=== wordID %s の全公演 %d件 ===" % (wid, len(recs)))
    for r in recs:
        print("  %s %s  %s（%s） %s" % (r["date"], (r["start"] or "")[:5],
                                        (r["name"] or "")[:40], r["pref"] or "", r["url"] or ""))
    if a.json:
        json.dump(recs, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("→ %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
