# -*- coding: utf-8 -*-
"""新着プール(genre:"new")で artist が「公演名の先頭1語で切れている」ものを洗い、
分かっているものは行置換で直す。

🚨 値だけの書き換えなので **行置換**（json.dumps で配列を作り直さない
   ＝feedback_index_html_crlf_preserve の2026-08-31項）。読み書きとも newline=''。

使い方:
  python tmp/fix_artist_0907.py           # 洗い出すだけ
  python tmp/fix_artist_0907.py --apply   # FIX に書いた分を直す
"""
import io, re, json, sys

PATH = "index.html"
APPLY = "--apply" in sys.argv

# e+の実ページで出演者を確認したもの
FIX = {
    6983: "五木ひろし",
}

src = io.open(PATH, encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", src, re.S).group(1))

# --- 洗い出し：artist が name の先頭1語（スペース区切り）と一致するもの ---
sus = []
for e in EV:
    if e.get("genre") != "new":
        continue
    a, n = (e.get("artist") or "").strip(), (e.get("name") or "").strip()
    if not a or not n:
        continue
    head = re.split(r"[ 　]", n)[0]
    if a == head and a != n:
        sus.append((e["id"], a, n[:56]))

with io.open("tmp/fix_artist_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 新着プールで artist が「公演名の先頭1語」と同じもの %d件 ===\n" % len(sus))
    f.write("（対バン名やイベント名が先頭に来ているだけの正常な子も混ざる＝実ページで見て決める）\n\n")
    for eid, a, n in sus:
        mark = "→ 直す: %s" % FIX[eid] if eid in FIX else ""
        f.write("  id=%-6s artist=%-22s name=%s  %s\n" % (eid, a[:22], n, mark))

print("疑わしい %d件 → tmp/fix_artist_0907.txt" % len(sus))

if not APPLY:
    print("(--apply を付けると FIX の分だけ直す)")
    sys.exit(0)

# --- 行置換で直す ---
lines = src.split("\r\n")
cur = None
n_fixed = 0
for i, ln in enumerate(lines):
    m = re.match(r'\s*"id": (\d+),\s*$', ln)
    if m:
        cur = int(m.group(1))
        continue
    if cur in FIX:
        m2 = re.match(r'(\s*"artist": )(.*?)(,?)$', ln)
        if m2:
            lines[i] = m2.group(1) + json.dumps(FIX[cur], ensure_ascii=False) + m2.group(3)
            n_fixed += 1
            cur = None

assert n_fixed == len(FIX), "直した行 %d / 想定 %d" % (n_fixed, len(FIX))
io.open("index.html.bak_0907_artist", "w", encoding="utf-8", newline="").write(src)
io.open(PATH, "w", encoding="utf-8", newline="").write("\r\n".join(lines))

# --- 検算 ---
h = io.open(PATH, encoding="utf-8", newline="").read()
EV2 = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
by = {e["id"]: e for e in EV2}
for eid, want in FIX.items():
    got = by[eid].get("artist")
    print("id=%s artist=%r %s" % (eid, got, "OK" if got == want else "🚨ちがう"))
print("CRLF=%d bareLF=%d" % (h.count("\r\n"), len(re.findall(r"(?<!\r)\n", h))))
