# -*- coding: utf-8 -*-
"""並び順ロジックが git HEAD と一致するかをバイト単位で確かめる。
   前後を広く切り出すとEVENTS配列が混ざって必ず不一致になるので、関数本体だけを切る
   （feedback_index_html_crcrlf_trap の反省）。あわせて差分の内訳も出す。"""
import io, re, subprocess, sys

def nl(s):
    """比較用に改行を揃える。git show と現物で CRLF/LF が違うだけで
       『全部不一致』に見えるのを防ぐ（比べたいのは中身であって改行ではない）。"""
    return s.replace("\r\n", "\n").replace("\r", "\n")

head = nl(subprocess.run(["git", "show", "HEAD:index.html"], capture_output=True).stdout.decode("utf-8"))
cur = nl(io.open("index.html", encoding="utf-8", newline="").read())

BLOCKS = [
    ("EVENTS.sort", r"EVENTS\.sort\(\(a, b\) => \{.*?\n  \}\);"),
    ("saleStartPending", r"function saleStartPending\(t\) \{[\s\S]{0,1500}?\n  \}"),
    ("ticketSortKey", r"const ticketSortKey = \(t\) => \{[\s\S]{0,1500}?\n    \};"),
    ("NEW_ORDER定義", r"const NEW_ORDER = \[[^\]]*\];"),
    ("SORT_PRESALE", r"const SORT_PRESALE[^\n]*\n"),
]

o = io.open("tmp/fingerprint_0908.txt", "w", encoding="utf-8")
allok = True
for name, pat in BLOCKS:
    a = re.search(pat, head, re.S)
    b = re.search(pat, cur, re.S)
    if not a or not b:
        o.write("%-18s 見つからない（HEAD=%s 現物=%s）\n" % (name, bool(a), bool(b)))
        if name != "NEW_ORDER定義":
            allok = False
        continue
    same = (a.group(0) == b.group(0))
    if name == "NEW_ORDER定義":
        o.write("%-18s 中身は変わる想定（HEAD %d文字 / 現物 %d文字）\n"
                % (name, len(a.group(0)), len(b.group(0))))
        continue
    o.write("%-18s 一致=%s （%d文字）\n" % (name, same, len(b.group(0))))
    allok = allok and same

# 差分の内訳＝SSRブロックとEVENTS配列で何行動いたか
def count(s, pat):
    m = re.search(pat, s, re.S)
    return len(m.group(0).split("\n")) if m else 0

for label, pat in [("EVENTS配列", r"const EVENTS = \[.*?\];\r?\n"),
                   ("SSR(AI_SSR)", r"<!-- AI_SSR_START -->[\s\S]*?<!-- AI_SSR_END -->")]:
    o.write("%-18s HEAD %d行 → 現物 %d行\n" % (label, count(head, pat), count(cur, pat)))

o.write("\n総合: %s\n" % ("並び順ロジックはHEADと完全一致" if allok else "🚨要確認"))
o.close()
print("sort_logic_identical=%s -> tmp/fingerprint_0908.txt" % allok)
