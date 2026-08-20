# -*- coding: utf-8 -*-
"""新着プール66件を本ジャンルへ振り分ける（ユーザー「ふりわけて」2026-08-06）。

原則＝**ぴあカテゴリで記憶した `_genre` をそのまま `genre` に移す**（自分で再分類しない
＝[[project_vendor_genre_autoassign]]）。人が見たのは `_piaSub` が空/その他の10件だけ。
そのうち下書きが実態と違った2件だけ直す:
  雷獣チャンネル THE LIVE「PLAY」 engeki → youtuber（YouTuberグループ「雷獣」のライブ）
  パンタレイ                    fes → dento＋engeki（太鼓演奏家・山部泰嗣の舞台／屋内なのでfesではない
                                 ＝[[feedback_fes_definition]]／迷うので両方方式=[[feedback_genre_both_when_unclear]]）
適用後は下書きキー(_genre/_extraGenres/_piaSub)を消し、NEW_ORDER を空にする。
"""
import json, re, io, sys, shutil, os, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_assign"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

# 名前で指定（idで書くと後から読めない＝[[feedback_entry_name_with_id]]）
OVERRIDE = {
    "雷獣チャンネル THE LIVE「PLAY」": ("youtuber", []),
    "パンタレイ": ("dento", ["engeki"]),
}

pool = [e for e in EVENTS if e.get("genre") == "new"]
print("プール %d件" % len(pool))

cnt = collections.Counter()
done = 0
for e in pool:
    name = e.get("artist") or ""
    if name in OVERRIDE:
        g, extra = OVERRIDE[name]
        print("  ✏️ %s ： %s → %s%s" % (name[:34], e.get("_genre"), g,
                                       ("＋" + ",".join(extra)) if extra else ""))
    else:
        g = e.get("_genre")
        extra = list(e.get("_extraGenres") or [])
    if not g or g == "new":
        sys.exit("下書きジャンルが無い: " + name)
    e["genre"] = g
    if extra:
        e["extraGenres"] = extra
    for k in ("_genre", "_extraGenres", "_piaSub"):
        e.pop(k, None)
    cnt[g + (("+" + ",".join(extra)) if extra else "")] += 1
    done += 1

# NEW_ORDER を空にする（配列だけ残ると新着タブが空のまま残る）
h2, n = re.subn(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]", r"\g<1>[]", h, count=1)
assert n == 1, "NEW_ORDER が見つからない"
m2 = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h2, re.S)

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h2[:m2.start()] + m2.group(1) + new_arr + m2.group(3) + h2[m2.end():])

print("\n振り分け %d件 / NEW_ORDER を空にした" % done)
for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]):
    print("  %-18s %d件" % (k, v))
