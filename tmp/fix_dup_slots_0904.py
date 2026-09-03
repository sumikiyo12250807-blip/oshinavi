# -*- coding: utf-8 -*-
"""二重登録の除去＝「url無しの枠」で、同じ(type, date, startDate)を持つ「url有りの枠」が
同じエントリ内にあるものだけを消す。飛び先URLが違う枠は絶対に触らない。

対象は 3735 / 3752 / 5516 の3件のみ（3370はbundleと個別eventCdで飛び先が違うので保留）。
改行はCRLFのまま保つ（[[feedback_index_html_crlf_preserve]]）。

🚨書き戻す前に「今のEVENTSテキスト == json.dumps(パース結果)」を確かめる。
   一致しなければ書式が変わってしまうので中止する。

  python tmp/fix_dup_slots_0904.py          # 下見
  python tmp/fix_dup_slots_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
TARGET_IDS = [3735, 3752, 5516]
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)

# --- 書式の往復チェック（LFに正規化して比べる） ---
def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)

roundtrip = dump(events)
if roundtrip != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式が一致しない（json.dumps では元の形に戻せない）")
    a, b = roundtrip, src_text.replace("\r\n", "\n")
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            print("  最初の相違 pos=%d" % i)
            print("  dumps : %r" % a[max(0, i - 60):i + 60])
            print("  actual: %r" % b[max(0, i - 60):i + 60])
            break
    else:
        print("  長さ違い dumps=%d actual=%d" % (len(a), len(b)))
    sys.exit(1)
print("OK: 書式の往復チェック通過")

removed = []
for e in events:
    if e.get("id") not in TARGET_IDS:
        continue
    ts = e.get("tickets", [])
    # 判定キーは (type, date)。startDate は build で取れたり取れなかったりするので鍵にしない。
    withurl = {}
    for t in ts:
        if t.get("url"):
            withurl.setdefault((t.get("type"), t.get("date")), t)
    keep, drop = [], []
    for t in ts:
        k = (t.get("type"), t.get("date"))
        if (not t.get("url")) and k in withurl:
            # 消す側が startDate を持っていて残す側に無ければ引き継ぐ
            survivor = withurl[k]
            if t.get("startDate") and not survivor.get("startDate"):
                survivor["startDate"] = t["startDate"]
            drop.append(t)
        else:
            keep.append(t)
    for t in drop:
        removed.append((e.get("id"), t.get("date")))
    e["tickets"] = keep

print("REMOVE_SLOTS=%d" % len(removed))
for eid, dt in removed:
    print("  id=%s slot_date=%s" % (eid, dt))
for e in events:
    if e.get("id") in TARGET_IDS:
        ts = e.get("tickets", [])
        print("  AFTER id=%s slots=%d with_url=%d" % (
            e.get("id"), len(ts), sum(1 for t in ts if t.get("url"))))

if not APPLY:
    print("(下見のみ。--apply で書き込み)")
    sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_dupfix")
new_text = dump(events).replace("\n", "\r\n")
out = raw[:m.start(1)] + new_text + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_dupfix)")
