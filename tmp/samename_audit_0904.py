# -*- coding: utf-8 -*-
"""A群「頭一致」の誤マッチ検算。
   既存名が短いと別アーティストの頭に刺さる（実例＝既存「yama」がぴあ「YAMATO String Quartet」に一致）。
   ぴあ名から既存名を取り除いた"残り"を見て、危ないものだけ抜き出す。"""
import json, re, io, unicodedata

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = []
for e in events:
    if e.get("genre") == "new":
        continue
    for f in ("artist", "name"):
        v = e.get(f)
        if v:
            ex.append((norm(v), e, v))

cand = json.load(io.open("tmp/_triage_0903.json", encoding="utf-8"))["samename"]

safe, risky = [], []
for it in cand:
    k = norm(it.get("artist"))
    if not k:
        continue
    hits = [(n, e, raw) for n, e, raw in ex if n and k.startswith(n)]
    ids = sorted(set(e.get("id") for _, e, _ in hits))
    if len(ids) != 1:
        continue
    n, e, raw = max(hits, key=lambda x: len(x[0]))
    rest = k[len(n):]
    # 危険サイン＝既存名が4文字以下、または残りが長い（＝別の名前が続いている疑い）
    danger = bool(rest) and ((len(n) <= 4) or (len(rest) >= len(n)))
    (risky if danger else safe).append((it, e, raw, rest))

buf = []
for tag, g in (("🚨要確認（既存名が短い or 残りが長い）", risky), ("✅そのまま統合してよさそう", safe)):
    buf.append("=" * 74)
    buf.append("【%s】 %d件" % (tag, len(g)))
    for it, e, raw, rest in g:
        buf.append("  ぴあ: %s" % (it.get("artist") or "")[:60])
        buf.append("  既存: id%s 「%s」  → 差分の残り: 「%s」" % (e.get("id"), raw[:40], rest[:40]))
        buf.append("        公演%s %s %s / %s" % (it.get("perfdate"), it.get("pref"),
                                                 it.get("venue"), it.get("url")))
io.open("tmp/samename_audit_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("RISKY=%d  SAFE=%d" % (len(risky), len(safe)))
print("WROTE tmp/samename_audit_0904.txt")
