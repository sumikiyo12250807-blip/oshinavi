# -*- coding: utf-8 -*-
"""「解析不能」36件について data-event-json を辿り、生きた公演を落としていないか確かめる。

🚨 ハーベスタは「読めなかった」も「買える枠が無い」も同じ扱いで落としている。
   ここでは **公演日が未来か** と **販売期間が今日を含むか** を実データで見る。
"""
import io, re, sys, json, time, html, datetime, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TODAY = datetime.date(2026, 9, 8)


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "replace")


def iso_date(s):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(s) or "")
    return datetime.date(*map(int, m.groups())) if m else None


urls = [u.strip() for u in io.open("tmp/rakuten_unparsed_0908.txt", encoding="utf-8") if u.strip()]
o = io.open("tmp/rk_json_all_0908.md", "w", encoding="utf-8")
o.write("# 「解析不能」の中身を data-event-json で確かめる（today=%s）\n\n" % TODAY)
o.write("| # | ページ | 公演名 | 公演日 | 会場/県 | 販売期間 | 判定 |\n|---|---|---|---|---|---|---|\n")

alive, past, nojson, err = 0, 0, 0, 0
alive_rows = []
for i, u in enumerate(urls, 1):
    tag = u.rstrip("/").split("/")[-1]
    try:
        h = get(u)
    except Exception as ex:
        o.write("| %d | %s | | | | | 取得失敗 |\n" % (i, tag)); err += 1; time.sleep(1); continue

    m = re.search(r"data-event-json=(\"|')(.*?)\1", h, re.S)
    if not m:
        o.write("| %d | %s | | | | | data-event-json 無し |\n" % (i, tag)); nojson += 1; time.sleep(1); continue

    ju = html.unescape(m.group(2)).strip()
    if not ju.startswith("http"):
        o.write("| %d | %s | | | | | JSONのURLでない |\n" % (i, tag)); nojson += 1; time.sleep(1); continue
    try:
        d = json.loads(get(ju))
    except Exception as ex:
        o.write("| %d | %s | | | | | JSONが読めない |\n" % (i, tag)); err += 1; time.sleep(1); continue

    ds = [iso_date(x) for x in (d.get("dates") or [])]
    ds = [x for x in ds if x]
    last = max(ds) if ds else None
    vs = d.get("venues") or []
    vtxt = "／".join("%s(%s)" % (v.get("name", ""), v.get("prefecture", "")) for v in vs[:2])

    sales = d.get("sales") or []
    stxt, sale_open = [], False
    for s in sales[:3]:
        a, b = s.get("startAt") or s.get("start") or "", s.get("endAt") or s.get("end") or ""
        stxt.append("%s〜%s" % (str(a)[:10], str(b)[:10]))
        sa, sb = iso_date(a), iso_date(b)
        if (sa is None or sa <= TODAY) and (sb is None or sb >= TODAY):
            sale_open = True

    if last and last >= TODAY:
        judge = "🚨公演が未来" + ("・販売中" if sale_open else "")
        alive += 1
        alive_rows.append((tag, d.get("title", ""), last, vtxt, u))
    else:
        judge = "公演が過去＝落として正しい"
        past += 1

    o.write("| %d | %s | %s | %s | %s | %s | %s |\n"
            % (i, tag, (d.get("title") or "")[:24], last, vtxt[:28], " / ".join(stxt)[:34], judge))
    time.sleep(1)

o.write("\n## まとめ\n\n")
o.write("- 🚨**公演が未来＝落としてはいけなかった … %d件**\n" % alive)
o.write("- 公演が過去＝落として正しい … %d件\n" % past)
o.write("- data-event-json が無い … %d件\n" % nojson)
o.write("- 取得/解析に失敗 … %d件\n" % err)
if alive_rows:
    o.write("\n### 拾い直すべきページ\n\n")
    for tag, title, last, vtxt, u in alive_rows:
        o.write("- **%s**（%s・%s）%s\n  %s\n" % (title[:40], last, vtxt[:30], tag, u))
o.close()
print("alive=%d past=%d nojson=%d err=%d -> tmp/rk_json_all_0908.md" % (alive, past, nojson, err))
