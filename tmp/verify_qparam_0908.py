# -*- coding: utf-8 -*-
"""?q= を足した後の index.html を機械で点検する。
 ①改行（CRLF / bareLF / CRCRLF）②EVENTS件数 ③並び順ロジックがバックアップと同一か"""
import io, re, sys

CUR = "index.html"
BAK = "index.html.bak_0908_qparam"

cur = open(CUR, "rb").read()
bak = open(BAK, "rb").read()

def counts(b):
    crlf = b.count(b"\r\n")
    crcrlf = b.count(b"\r\r\n")
    bare_lf = b.count(b"\n") - crlf
    lone_cr = b.count(b"\r") - b.count(b"\r\n")
    return crlf, bare_lf, crcrlf, lone_cr

out = io.open("tmp/verify_qparam_0908.txt", "w", encoding="utf-8")
W = out.write

c = counts(cur); k = counts(bak)
W("=== 改行 ===\n")
W("           CRLF      bareLF  CRCRLF  孤立CR\n")
W("変更前  %9d %8d %7d %6d\n" % k)
W("変更後  %9d %8d %7d %6d\n" % c)
ok_nl = (c[1] == 0 and c[2] == 0 and c[3] == 0 and c[0] >= k[0])
W("判定: %s\n\n" % ("OK（bareLF/CRCRLF/孤立CR がすべて0）" if ok_nl else "🚨NG"))

# EVENTS 件数
def n_events(b):
    s = b.decode("utf-8")
    m = re.search(r"const EVENTS\s*=\s*(\[.*?\]);\s*\n", s, re.S)
    import json
    return len(json.loads(m.group(1)))

ne_cur, ne_bak = n_events(cur), n_events(bak)
W("=== EVENTS 件数 ===\n変更前 %d / 変更後 %d → %s\n\n"
  % (ne_bak, ne_cur, "OK" if ne_cur == ne_bak else "🚨NG"))

# 並び順ロジックの指紋（sort_guard が見ているブロック）
def fingerprint(b):
    s = b.decode("utf-8")
    out = {}
    for key, pat in [
        ("EVENTS.sort", r"EVENTS\.sort\(\(a, b\) => \{.{0,4000}?\n  \}\);"),
        ("saleStartPending", r"saleStartPending.{0,1500}?\n"),
        ("SORT_PRESALE", r"const SORT_PRESALE.{0,200}?\n"),
        ("NEW_ORDER", r"NEW_ORDER.{0,300}?\n"),
    ]:
        m = re.search(pat, s, re.S)
        out[key] = m.group(0) if m else None
    return out

fc, fb = fingerprint(cur), fingerprint(bak)
W("=== 並び順まわりの指紋（バックアップと文字列比較）===\n")
all_ok = True
for k2 in fc:
    same = (fc[k2] == fb[k2])
    found = fc[k2] is not None
    all_ok = all_ok and same and found
    W("  %-18s 見つかった=%s  一致=%s\n" % (k2, found, same))
W("判定: %s\n\n" % ("OK（全ブロック一致）" if all_ok else "🚨NG"))

# 足したコードが1回だけ入っているか
s = cur.decode("utf-8")
n_q = s.count('URLSearchParams(location.search).get("q")')
W("=== 足したコード ===\n?q= の読み取り: %d か所（1が正）\n" % n_q)

W("\n総合: %s\n" % ("✅すべてOK" if (ok_nl and ne_cur == ne_bak and all_ok and n_q == 1) else "🚨要確認"))
out.close()
print("wrote tmp/verify_qparam_0908.txt  nl_ok=%s events_ok=%s sort_ok=%s q=%d"
      % (ok_nl, ne_cur == ne_bak, all_ok, n_q))
