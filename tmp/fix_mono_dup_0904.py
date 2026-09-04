# -*- coding: utf-8 -*-
"""id4500 MONO NO AWARE の神戸公演の二重登録を解消する。

ぴあ実ページ（eventCd=2628450）を開いて確認した事実：
  一般発売は【大阪公演】【京都公演】【奈良公演】【神戸公演】の**4枠だけ**（＋プレリザーブ2枠）。
うちのDBは同じURLから7枠を取っていて、神戸だけ
  「一般発売（兵庫 R9年 2/26公演）9/12 10:00発売」
  「一般発売【神戸公演】（兵庫 R9年 2/26公演）9/12 10:00発売」
の2つに割れている＝**重複**。

ぴあは4枠とも「【○○公演】一般発売」の形だが、うちのパーサーは大阪・京都・奈良では
その印を落としている。**表記を揃えるため【神戸公演】が付いているほうを消す**。

🚨これは check_dup_slots では拾えない型（券種名が違うのでA/B/Cのどれにも入らない）。
   ASKAの「紙チケット／電子チケット」のように**券種名が違って中身も別**の枠もあるので、
   機械で一律に畳んではいけない。**実ページを見て1件ずつ判断すること。**

  python tmp/fix_mono_dup_0904.py          # 下見
  python tmp/fix_mono_dup_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
TARGET = 4500
DROP_TYPE = "一般発売【神戸公演】（兵庫 R9年 2/26公演）9/12 10:00発売"
KEEP_TYPE = "一般発売（兵庫 R9年 2/26公演）9/12 10:00発売"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

e = next((x for x in events if x.get("id") == TARGET), None)
if not e:
    print("ABORT: id=%s が無い" % TARGET); sys.exit(1)

ts = e.get("tickets", [])
drop = [t for t in ts if t.get("type") == DROP_TYPE]
keep = [t for t in ts if t.get("type") == KEEP_TYPE]
print("消す候補=%d  残す枠=%d  （全%d枠）" % (len(drop), len(keep), len(ts)))
if len(drop) != 1 or len(keep) != 1:
    print("ABORT: 想定と違う（消す1・残す1でないと触らない）"); sys.exit(1)
if drop[0].get("url") != keep[0].get("url"):
    print("ABORT: URLが違う＝別の売り場かもしれない"); sys.exit(1)
if drop[0].get("date") != keep[0].get("date") or drop[0].get("startDate") != keep[0].get("startDate"):
    print("ABORT: 日付が違う"); sys.exit(1)
print("  同じURL・同じ受付終了日・同じ発売開始日を確認")

e["tickets"] = [t for t in ts if t is not drop[0]]
print("枠 %d -> %d" % (len(ts), len(e["tickets"])))

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_mono")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
