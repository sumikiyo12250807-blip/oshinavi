# -*- coding: utf-8 -*-
"""id7449 中部フィル 室内楽シリーズVol.6 を新着プールから外す。

理由＝ぴあの生HTMLの文言が **[貸切公演]** ＝一般に売っている枠が無い。
      チケットが1枚も無いカードを出すと「カードは出るのに買えない」型になる
      （feedback_zero_badge_gate）。投機的エントリは置かない（feedback_zero_tolerance）。
🚨これは削除ゲートの対象外＝**投入したその日のうちに、まだ振り分けていないプール分を戻すだけ**。
"""
import io, json, re, sys, datetime

sys.stdout.reconfigure(encoding="utf-8")
TARGET = 7449

h = io.open("index.html", encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
evs = json.loads(m.group(2))

hit = [e for e in evs if e["id"] == TARGET]
assert len(hit) == 1, hit
assert hit[0].get("genre") == "new", "振り分け済みのエントリは触らない"
assert not (hit[0].get("tickets") or []), "枠があるなら消さない"
print("外す: id%d %s ／ %s" % (TARGET, hit[0].get("name"), hit[0].get("date")))

evs = [e for e in evs if e["id"] != TARGET]

mo = re.search(r"(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]", h)
cur = [int(x) for x in re.findall(r"\d+", mo.group(2))]
assert TARGET in cur
new_order = "[" + ", ".join(str(i) for i in cur if i != TARGET) + "]"
h2, n = re.subn(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]", r"\g<1>" + new_order, h, count=1)
assert n == 1

bak = "index.html.bak_%s_drop7449" % datetime.date.today().strftime("%m%d")
io.open(bak, "w", encoding="utf-8", newline="").write(h)
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h2, re.S)
arr = json.dumps(evs, ensure_ascii=False, indent=2).replace("\n", NL)
io.open("index.html", "w", encoding="utf-8", newline="").write(
    h2[:m.start()] + m.group(1) + arr + m.group(3) + h2[m.end():])
print("総%d件 / NEW_ORDER %d件 (backup %s)" % (len(evs), len(cur) - 1, bak))

raw = open("index.html", "rb").read()
print("CRLF=%d bareLF=%d CRCRLF=%d loneCR=%d"
      % (raw.count(b"\r\n"), len(re.findall(rb"(?<!\r)\n", raw)),
         raw.count(b"\r\r\n"), len(re.findall(rb"\r(?!\n)", raw))))
