# -*- coding: utf-8 -*-
"""新着プールのジャンル下書き(_genre)を、ぴあの対応表どおりに直す。
別エージェントの独立検証で出た指摘のうち、**機械で決まるものだけ**を直す。

  6437 / 6442  engeki -> talkshow  … ぴあ「講演会・トークショー」。9/3に対応表を変えた後の写し漏れ
  6477         fes    -> classic   … ぴあ「クラシック/オーケストラ」。名前が「芸術祭」でもカテゴリに従う
                                     （[[feedback_fes_definition]]＝名前に祭が付くだけでfesにしない）
  6395         enka   -> hougaku   … 津軽三味線デュオ。道具も名前に三味線があればhougakuへ倒す設計
                                     （[[feedback_dento_split_music_stage]]＝三味線は「聴きに行く」側）

  python tmp/fix_pool_genre_0904.py          # 下見
  python tmp/fix_pool_genre_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
FIX = {6437: "talkshow", 6442: "talkshow", 6477: "classic", 6395: "hougaku"}
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

n = 0
for e in events:
    i = e.get("id")
    if i not in FIX:
        continue
    if e.get("genre") != "new":
        print("ABORT: id=%s はもう振り分け済み（genre=%s）" % (i, e.get("genre"))); sys.exit(1)
    print("id=%-5s _genre %s -> %s" % (i, e.get("_genre"), FIX[i]))
    e["_genre"] = FIX[i]
    n += 1
print("CHANGED=%d / %d" % (n, len(FIX)))
if n != len(FIX):
    print("ABORT: 対象が全部見つからない"); sys.exit(1)

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_poolgenre")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
