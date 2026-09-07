# -*- coding: utf-8 -*-
"""id710 島津亜矢の venue / prefecture を、実際に持っている枠の会場から作り直す。

枠を12足したのに venue が「全国ツアー（森のホール21／東京国際フォーラム）」・
prefecture が「千葉・東京」のままだった＝**都道府県で絞る人が見つけられない**。

会場名は ぴあ再ビルドの結果（tmp/built_shimazu_0907.json）と既存の venue から機械で集める。
県は ticket.type の「（◯◯ M/D公演）」から拾う。5県以上なら prefecture は「全国」
（build_pia_entries と同じ決まり）。
"""
import io, re, json, sys

APPLY = "--apply" in sys.argv
TARGET = 710

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
e = [x for x in EV if x["id"] == TARGET][0]

# ① 会場＝既存 venue の（）の中身 ＋ ビルド結果の venue
halls = []
m = re.search(r"全国ツアー（(.*)）", e.get("venue") or "")
if m:
    halls += [x.strip() for x in m.group(1).split("／") if x.strip()]
for b in json.load(io.open("tmp/built_shimazu_0907.json", encoding="utf-8")):
    v = b.get("venue") or ""
    v = re.sub(r"^全国ツアー（|）$", "", v)
    for x in v.split("／"):
        x = x.strip()
        if x and x not in halls:
            halls.append(x)

# ② 県＝券種名の「（◯◯ M/D公演）」から
prefs = []
for t in e.get("tickets", []):
    mp = re.search(r"（([^（）]*?)\s*(?:R9年\s*)?\d{1,2}/\d{1,2}", t.get("type") or "")
    if not mp:
        continue
    for p in mp.group(1).split("・"):
        p = p.strip()
        if p and p not in prefs:
            prefs.append(p)

venue = "全国ツアー（%s）" % "／".join(halls)
pref = "全国" if len(prefs) >= 5 else "・".join(prefs)
print("会場 %d件 / 県 %d件" % (len(halls), len(prefs)))
print("venue = %s" % venue[:100])
print("prefecture = %s  （%s）" % (pref, "・".join(prefs)))

if not APPLY:
    print("(--apply で書き込む)")
    sys.exit(0)

lines = h.split("\r\n")
cur, done = None, set()
for i, ln in enumerate(lines):
    m2 = re.match(r'\s*"id": (\d+),\s*$', ln)
    if m2:
        cur = int(m2.group(1))
        continue
    if cur == TARGET:
        for k, v in (("venue", venue), ("prefecture", pref)):
            m3 = re.match(r'(\s*"%s": )(.*?)(,?)$' % k, ln)
            if m3 and k not in done:
                lines[i] = m3.group(1) + json.dumps(v, ensure_ascii=False) + m3.group(3)
                done.add(k)

assert done == {"venue", "prefecture"}, "書き換えられなかった: %s" % ({"venue", "prefecture"} - done)
io.open("index.html.bak_0907_venue710", "w", encoding="utf-8", newline="").write(h)
io.open("index.html", "w", encoding="utf-8", newline="").write("\r\n".join(lines))

h2 = io.open("index.html", encoding="utf-8", newline="").read()
EV2 = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h2, re.S).group(1))
e2 = [x for x in EV2 if x["id"] == TARGET][0]
print("検算 venue=%s / prefecture=%s" % (e2["venue"][:60], e2["prefecture"]))
print("CRLF=%d bareLF=%d" % (h2.count("\r\n"), len(re.findall(r"(?<!\r)\n", h2))))
