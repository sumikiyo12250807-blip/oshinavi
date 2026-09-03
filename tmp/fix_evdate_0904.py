# -*- coding: utf-8 -*-
"""統合で会場を足したのに entry.date（千秋楽）を更新していないエントリを直す。

reconcile の ❌QC-EVDATE が「ev.date=X が実公演の千秋楽Yより古い＝画面から消える」と教えてくれるので、
その Y を entry.date に入れ、dateLabel の日付部分も作り直す。
（[[feedback_tour_consolidate]]＝ツアーは1エントリ・dateは千秋楽）

  python tmp/fix_evdate_0904.py          # 下見
  python tmp/fix_evdate_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil, datetime

PATH = "index.html"
LOG = "tmp/recon_merged_0904.txt"
APPLY = "--apply" in sys.argv

# reconcile の出力を「id行 → その下にぶら下がるQC-EVDATE」で対応づける
cur = None
fix = {}
for ln in io.open(LOG, encoding="utf-8"):
    m = re.match(r"^[^\s]*\s*id=(\d+)\s", ln)
    if m:
        cur = int(m.group(1)); continue
    m2 = re.search(r"QC-EVDATE ev\.date=(\d{4}-\d{2}-\d{2}) が実公演の千秋楽(\d{4}-\d{2}-\d{2})より古い", ln)
    if m2 and cur:
        old, new = m2.group(1), m2.group(2)
        # 同じidに複数出たら、いちばん遅い千秋楽を採る
        if cur not in fix or new > fix[cur][1]:
            fix[cur] = (old, new)

print("QC_EVDATE_ENTRIES=%d" % len(fix))

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

WD = "月火水木金土日"


def jp(d):
    y, mo, da = (int(x) for x in d.split("-"))
    w = WD[datetime.date(y, mo, da).weekday()]
    ys = "R9年 " if y == 2027 else ""
    return "%d年%d月%d日(%s)" % (y, mo, da, w), ys


by_id = {e.get("id"): e for e in events}
n, skipped, need_label = 0, [], []
buf = ["entry.date（千秋楽）の更新 2026-09-04", ""]
for i, (old, new) in sorted(fix.items()):
    e = by_id.get(i)
    if not e:
        skipped.append((i, "エントリが無い")); continue
    if (e.get("date") or "") != old:
        skipped.append((i, "date が %s でなく %s" % (old, e.get("date")))); continue
    if new <= old:
        skipped.append((i, "新しい千秋楽が古い")); continue
    lab = e.get("dateLabel") or ""
    jpnew, _ = jp(new)
    # 🚨ラベルは形が多様（会場を列挙する形・曜日なしの形がある）。
    #   「〜YYYY年M月D日(曜)」が**ちょうど1つ**ある形だけ機械で差し替え、
    #   それ以外は date だけ直して「ラベル要修正」に出す（形を壊す方が害が大きい）。
    hits = re.findall(r"〜(\d{4}年\d{1,2}月\d{1,2}日\([月火水木金土日]\))", lab)
    if len(hits) == 1:
        newlab = lab.replace("〜" + hits[0], "〜" + jpnew, 1)
        e["dateLabel"] = newlab
        buf.append("- id%s %s : date %s -> %s" % (i, e.get("name"), old, new))
        buf.append("    label: %s" % lab)
        buf.append("        -> %s" % newlab)
    else:
        need_label.append((i, e.get("name"), lab, new))
        buf.append("- id%s %s : date %s -> %s  ⚠️ラベルは形が特殊なので触っていない" % (
            i, e.get("name"), old, new))
        buf.append("    label(そのまま): %s" % lab)
    e["date"] = new
    n += 1

print("FIXED=%d  SKIPPED=%d  LABEL_NEEDS_HAND=%d" % (n, len(skipped), len(need_label)))
for i, why in skipped:
    print("  skip id=%s %s" % (i, why))
io.open("tmp/fix_evdate_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_evdate")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
