# -*- coding: utf-8 -*-
"""楽天の組み立て22件を、**投入する前に**既存と突き合わせる。

🚨memoryが名指しで警告している型が2つある（[[reference_rakuten_harvest]] 罠の節）:
  ① 同じ興行が会場ごとに別ページ＝「〜 in 岐阜」「〜 in 仙台」でカードが乱立する
     （[[feedback_tour_consolidate]]）
  ② 別名の既存とかぶる＝「ANA presents ナーポオケラ」vs 既存「Na Pookela ナーポオケラ」
     名前だけの名寄せでは落ちる → **会場＋公演日**で見る（[[feedback_check_duplicates]]）

判定は機械で出すだけ。畳むかどうかは中身を見て決める。
"""
import io, json, re, sys, unicodedata

sys.stdout.reconfigure(encoding="utf-8")


def vkey(v):
    s = unicodedata.normalize("NFKC", v or "")
    s = re.sub(r"[〔（(\[].*?[〕）)\]]", "", s)
    return re.sub(r"[\s　・]", "", s)


def nkey(n):
    """会場・エリアの角括弧と『in ○○』の尻尾を落とした名前キー"""
    s = unicodedata.normalize("NFKC", n or "")
    s = re.sub(r"[［\[].*?[］\]]", "", s)
    s = re.sub(r"\s*in\s*[^\s]+$", "", s, flags=re.I)
    return re.sub(r"[\s　・「」『』〜~－\-]", "", s).lower()


s = io.open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))
new = json.load(io.open("tmp/built_rakuten_0908.json", encoding="utf-8"))

# 既存の索引（会場キー→id / 名前キー→id）
by_venue, by_name = {}, {}
for e in EV:
    for v in re.split(r"[／/]", re.sub(r"^全国ツアー（(.*)）$", r"\1", e.get("venue") or "")):
        if vkey(v):
            by_venue.setdefault(vkey(v), []).append(e)
    if nkey(e.get("name")):
        by_name.setdefault(nkey(e.get("name")), []).append(e)

print("=== 投入前の重複チェック（22件）===\n")
flag = 0
for n in new:
    hits = []
    nk = nkey(n.get("name"))
    for e in by_name.get(nk, []):
        hits.append(("名前が一致", e))
    for v in re.split(r"[／/]", re.sub(r"^全国ツアー（(.*)）$", r"\1", n.get("venue") or "")):
        for e in by_venue.get(vkey(v), []):
            if e.get("date") == n.get("date"):
                hits.append(("会場＋公演日が一致", e))
    # 名前の部分一致（片方がもう片方を含む）＝別名義の疑い
    for k, es in by_name.items():
        if k and nk and k != nk and (k in nk or nk in k) and min(len(k), len(nk)) >= 6:
            for e in es:
                hits.append(("名前が包含関係", e))

    seen, uniq = set(), []
    for why, e in hits:
        if e["id"] in seen:
            continue
        seen.add(e["id"]); uniq.append((why, e))
    if not uniq:
        continue
    flag += 1
    print("\U0001f6a8 new id%d %s" % (n["id"], n["name"][:50]))
    print("     %s ／ %s ／ %s" % (n.get("date"), n.get("prefecture"), n.get("venue")[:60]))
    for why, e in uniq:
        print("   ← 既存 id%-5s [%s] %s" % (e["id"], why, (e.get("name") or "")[:46]))
        print("        %s ／ %s ／ %s" % (e.get("date"), e.get("prefecture"), (e.get("venue") or "")[:60]))
    print()

print("疑いあり %d件 / 22件" % flag)
