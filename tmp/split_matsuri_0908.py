# -*- coding: utf-8 -*-
"""id3224 MATSURI から、別公演の枠を1つ切り出す（エントリ分割）。

【何が起きていたか】
  id3224「MATSURI」（全国ツアー・楽天）に
  「一般発売（東京 12/2公演）10/3 10:00発売」という **url が空の枠**が混ざっていた。
  楽天の実ページに 12/2 も 10/3 も無く、ぴあを名前で引いたら別物だった＝
  **「THE MATSURI SESSION」12/2 豊洲PIT**（eventCd=2631679）。
  会場一覧にも豊洲PITは入っていない＝ツアーの一部ではなく、まぎれ込んだ枠。

【やること】
  ① id3224 からその枠を外す（他の枠には触らない）
  ② THE MATSURI SESSION を**別エントリ**として新着プールへ入れる
     （[[feedback_terminology_batch_split]] 分割＝エントリ分割）

🚨index.html は「テキストで読んでテキストで書く」（[[feedback_index_html_crlf_preserve]]）。
"""
import io, json, re, sys, datetime

sys.stdout.reconfigure(encoding="utf-8")

BAD = "一般発売（東京 12/2公演）10/3 10:00発売"

h = io.open("index.html", encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EV = json.loads(m.group(2))
by = {e["id"]: e for e in EV}

# ① 混ざっていた枠を外す
e = by[3224]
before = len(e["tickets"])
hit = [t for t in e["tickets"] if t.get("type") == BAD]
assert len(hit) == 1, hit
assert not (hit[0].get("url") or ""), "URLを持つ枠は外さない"
e["tickets"] = [t for t in e["tickets"] if t.get("type") != BAD]
print("id3224 MATSURI: %d枠 → %d枠（外した＝%s）" % (before, len(e["tickets"]), BAD))
assert len(e["tickets"]) >= 1, "枠が0になるなら外さない"

# ② 別エントリとして投入
new = json.load(io.open("tmp/built_matsuri_0908.json", encoding="utf-8"))
assert len(new) == 1
nid = max(x["id"] for x in EV) + 1
new[0]["id"] = nid
assert new[0].get("genre") == "new"
EV.append(new[0])
print("新エントリ id%d %s ／ %s ／ %s"
      % (nid, new[0]["name"], new[0]["date"], new[0]["venue"]))
for t in new[0]["tickets"]:
    print("   + %s" % t["type"])

mo = re.search(r"(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]", h)
cur = [int(x) for x in re.findall(r"\d+", mo.group(2))]
h2, n = re.subn(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]",
                r"\g<1>" + "[" + ", ".join(str(i) for i in cur + [nid]) + "]", h, count=1)
assert n == 1

bak = "index.html.bak_%s_matsuri" % datetime.date.today().strftime("%m%d")
io.open(bak, "w", encoding="utf-8", newline="").write(h)
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h2, re.S)
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace("\n", NL)
io.open("index.html", "w", encoding="utf-8", newline="").write(
    h2[:m.start()] + m.group(1) + arr + m.group(3) + h2[m.end():])
print("総%d件 / NEW_ORDER %d件 (backup %s)" % (len(EV), len(cur) + 1, bak))

raw = open("index.html", "rb").read()
print("CRLF=%d bareLF=%d CRCRLF=%d loneCR=%d"
      % (raw.count(b"\r\n"), len(re.findall(rb"(?<!\r)\n", raw)),
         raw.count(b"\r\r\n"), len(re.findall(rb"\r(?!\n)", raw))))
