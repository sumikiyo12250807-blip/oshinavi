# -*- coding: utf-8 -*-
"""id2776 Fear,and Loathing in Las Vegas をツアー化して全枠を入れる。
バイナリで読み、該当エントリのブロックだけ差し替える（CRLF維持）。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PATH = r"C:\Users\user\oshinavi\index.html"

P = "https://t.pia.jp/pia/event/event.do?eventCd=%s"

TICKETS = [
    # 8/1 10:00発売の発売前6枠（startDate==date＝ぴあが締切未掲出の単日形）
    ("一般発売（宮城 11/1公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2627622"),
    ("一般発売（京都 11/13公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2627049"),
    ("一般発売（愛知 11/19公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2628029"),
    ("一般発売（東京 11/27公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2630548"),
    ("一般発売（福岡 12/3公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2630358"),
    ("一般発売（大阪 R9年1/23公演）8/1 10:00発売", "2026-08-01", "2026-08-01", "2627049"),
    # すでに受付中の枠（締切あり）
    ("一般発売（京都 9/26公演）〜9/10 23:59", "2026-09-10", None, "2611992"),
]

data = open(PATH, "rb").read()
text = data.decode("utf-8")

m = re.search(r'\n  \{\r?\n    "id": 2776,.*?\r?\n  \},', text, re.S)
if not m:
    print("!! id=2776 のブロックが見つからない")
    sys.exit(1)

block = m.group(0)
ev = json.loads(block.strip().lstrip("{").rjust(0) or "{}") if False else None
# ブロックからJSON本体だけ取り出す
jtxt = block.strip()
if jtxt.endswith(","):
    jtxt = jtxt[:-1]
ev = json.loads(jtxt)

print("変更前: date=%s tickets=%d" % (ev["date"], len(ev["tickets"])))

ev["date"] = "2027-01-23"                     # 千秋楽（大阪 GORILLA HALL）
ev["dateLabel"] = "2026年11月1日(日)〜2027年1月23日(土) 全国ツアー"
ev["venue"] = "全国ツアー（仙台Rensa／KYOTO MUSE／ダイアモンドホール／Zepp Haneda（TOKYO）／DRUM LOGOS／GORILLA HALL OSAKA／KBSホール）"
ev["prefecture"] = "全国"

tickets = []
for typ, d, sd, cd in TICKETS:
    t = {"type": typ, "date": d}
    if sd:
        t["startDate"] = sd
    t["url"] = P % cd
    tickets.append(t)
ev["tickets"] = tickets
ev["verifiedAt"] = "2026-08-01"

new_json = json.dumps(ev, ensure_ascii=False, indent=2)
new_block = "\n  " + new_json.replace("\n", "\n  ") + ","
# ここで作った改行はLFなので、最後にファイル全体でCRLFへ畳み直す
text = text[:m.start()] + new_block + text[m.end():]

out = text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
open(PATH, "wb").write(out)

crlf = out.count(b"\r\n")
stray = out.count(b"\n") - crlf
print("変更後: date=%s tickets=%d" % (ev["date"], len(ev["tickets"])))
print("CRLF=%d stray_LF=%d" % (crlf, stray))
