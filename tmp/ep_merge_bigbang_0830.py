# -*- coding: utf-8 -*-
"""① 東西ビッグバンの大阪編を、東京編のエントリ(id6000)に**枠として足す**（ユーザー決定：同じエントリ）。"""
import datetime, importlib.util, io, json, re, shutil, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TODAY = datetime.date.today()

def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp); argv = sys.argv; sys.argv = [path, "__lib__"]
    try: sp.loader.exec_module(m)
    except SystemExit: pass
    finally: sys.argv = argv
    return m

eh = load("eh", "tools/eplus_harvest.py")
OSAKA = "https://eplus.jp/sf/detail/4563250001-P0030001P021001"

P = "index.html"
src = io.open(P, encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S)
EVENTS = json.loads(m.group(2)); byid = {e["id"]: e for e in EVENTS}
e = byid[6000]

have = {re.sub(r"\?.*$", "", t.get("url") or "") for t in e.get("tickets", [])}
added = 0
if re.sub(r"\?.*$", "", OSAKA) not in have:
    h = eh.fetch(OSAKA); time.sleep(0.4)
    iso, tm = "2026-09-14", "17:00"
    for w in [w for w in eh.parse_windows(h) if w["ed"] >= TODAY]:
        same_day = (str(w["ed"]) == iso)
        sess = (" %s公演" % tm) if same_day else "公演"
        lab = re.sub(r"\s+", "", w["label"]) or ((w["kind"] or "先着") + "一般発売")
        if w["sd"] >= TODAY:
            typ = "%s（大阪府 9/14%s）%d/%d %s発売" % (lab, sess, w["sd"].month, w["sd"].day, w["st"])
            tk = {"type": typ, "date": str(w["ed"]), "url": OSAKA, "startDate": str(w["sd"])}
        else:
            typ = "%s（大阪府 9/14%s）〜%d/%d %s" % (lab, sess, w["ed"].month, w["ed"].day, w["et"])
            tk = {"type": typ, "date": str(w["ed"]), "url": OSAKA}
        e["tickets"].append(tk); added += 1
        print("  +", typ)
    if added:
        e["venue"] = "全国ツアー（心斎橋CLAPPER／Live House 獅子王）"
        e["prefecture"] = "大阪・東京"
        e["dateLabel"] = "2026年9月14日(月)〜2026年10月19日(月) 大阪・東京"
        e["name"] = "透明少女×モザヰク×ハオ「東西ビッグバン」大阪編・東京編"
else:
    print("  すでに登録済み")

shutil.copy(P, "index.html.bak_0830_bigbang")
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
arr = "\n".join("  " + l if i else l for i, l in enumerate(arr.split("\n")))
out = src[:m.start(2)] + arr + src[m.end(2):]
if "\r\n" in src: out = out.replace("\r\n", "\n").replace("\n", "\r\n")
io.open(P, "w", encoding="utf-8", newline="").write(out)
print("① 東西ビッグバンに +%d枠（1エントリに統合）" % added)
