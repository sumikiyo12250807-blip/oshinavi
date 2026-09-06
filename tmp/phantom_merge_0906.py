# -*- coding: utf-8 -*-
"""劇団四季「オペラ座の怪人」名古屋 の3エントリを 4625 に畳む（第1段：4625の中身を作り直す）。

4625「1月／名古屋」・4627「3月／名古屋」・7045「／名古屋」は、
おなじ会場（MTG名古屋四季劇場）・おなじ千秋楽（2027-03-31）の同じロングラン公演。

枠は ぴあの実ページ（bundle b2666606 と 各eventCd）から機械で取り直した：
  受付中6枠のみ。【ぴあスペシャルシートS1席】の3枠(2633222/2633227/2633229)は
  bundleに現れず、個別eventCdでも [受付終了]（2つの独立した確認が一致）→ 落とす。
飛び先URLは 4625 が持っていた**月ごとの個別eventCd**を残す（bundleより具体的なので）。

🚨 EVENTS配列を作り直さない。4625 の artist/name/tickets の行だけを差し替える。
   （[[feedback_index_html_crlf_preserve]] 2026-08-31項）
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

PATH = "index.html"
TARGET = 4625

NEW_ARTIST = '劇団四季「オペラ座の怪人」／名古屋'
NEW_TICKETS = [
    ('一般発売（愛知 10/1〜10/31公演）〜10/29 23:59', '2026-10-29', None, '2604197'),
    ('一般発売（愛知 11/1〜11/29公演）〜11/27 23:59', '2026-11-27', None, '2604198'),
    ('一般発売（愛知 12/1〜12/31公演）〜12/29 23:59', '2026-12-29', None, '2604200'),
    ('一般発売（愛知 R9年 1/1〜1/31公演）〜1/29 23:59', '2027-01-29', '2026-09-06', '2624195'),
    ('一般発売（愛知 R9年 2/5〜2/28公演）〜2/26 23:59', '2027-02-26', '2026-09-06', '2624196'),
    ('一般発売（愛知 R9年 3/3〜3/31公演）〜3/29 23:59', '2027-03-29', '2026-09-06', '2624197'),
]
BASE = 'https://t.pia.jp/pia/event/event.do?eventCd='

with io.open(PATH, encoding="utf-8", newline="") as f:
    lines = f.read().split("\n")

# 対象エントリの行範囲を見つける
start = None
for i, ln in enumerate(lines):
    if re.match(r'^\s*"id":\s*%d,\s*\r?$' % TARGET, ln):
        start = i
        break
assert start is not None, "id=%d が見つからない" % TARGET

# tickets の開始行と終了行（インデントが同じ "]," の行）
tk_open = None
for i in range(start, start + 400):
    if re.match(r'^(\s*)"tickets":\s*\[\s*\r?$', lines[i]):
        tk_open = i
        indent = re.match(r'^(\s*)', lines[i]).group(1)
        break
assert tk_open is not None, "tickets が見つからない"
tk_close = None
for i in range(tk_open + 1, tk_open + 400):
    if lines[i].rstrip("\r") == indent + "],":
        tk_close = i
        break
assert tk_close is not None, "tickets の閉じが見つからない"

inner = indent + "  "
block = []
for n, (typ, date, sdate, cd) in enumerate(NEW_TICKETS):
    block.append(inner + "{")
    block.append(inner + '  "type": "%s",' % typ)
    block.append(inner + '  "date": "%s",' % date)
    if sdate:
        block.append(inner + '  "startDate": "%s",' % sdate)
    block.append(inner + '  "url": "%s%s"' % (BASE, cd))
    block.append(inner + ("}," if n < len(NEW_TICKETS) - 1 else "}"))

old_count = sum(1 for ln in lines[tk_open:tk_close] if ln.strip() == "{")
lines[tk_open + 1:tk_close] = [b + "\r" for b in block]

# artist / name を「月」なしの名前に直す
for i in range(start, start + 8):
    m = re.match(r'^(\s*"(?:artist|name)":\s*)(".*?")(,\s*\r?)$', lines[i])
    if m:
        lines[i] = m.group(1) + '"%s"' % NEW_ARTIST + m.group(3)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(lines))

print("id=%d の枠を %d → %d に作り直した" % (TARGET, old_count, len(NEW_TICKETS)))
print("artist/name → %s" % NEW_ARTIST)
