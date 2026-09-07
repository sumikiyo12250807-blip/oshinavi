import io, re, sys, os
d = r"C:\Users\user\oshinavi\tmp\x0907"
out = []
for i in range(1, 8):
    p = os.path.join(d, f"post{i}.txt")
    t = io.open(p, encoding="utf-8").read()
    lines = t.rstrip("\n").split("\n")
    n = len(t.rstrip("\n"))
    ok_head = lines[0] == 'OSHINAVIの"9/8チケット発売"ピックアップ🎫'
    ok_tag = lines[-1] == "#OSHINAVI #明日発売 #チケット"
    # 。 followed by non-newline (except モーニング娘。)
    bad_kuten = [ln for ln in lines if re.search(r"(?<!モーニング娘)。(?!$)", ln)]
    ok_cta = "▼チケット情報はこちら\noshinavi.jp" in t
    bad_url = bool(re.search(r"https?://|\?x=", t))
    banned = [w for w in ["あんた", "生で浴びる", "押さえ", "おさえ"] if w in t]
    out.append(f"post{i}: len={n} head={ok_head} tag={ok_tag} cta={ok_cta} badurl={bad_url} banned={banned} kuten_bad={len(bad_kuten)}")
    for b in bad_kuten:
        out.append("   KUTEN: " + b)
io.open(os.path.join(d, "check_result.txt"), "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out).encode("ascii", "replace").decode())
