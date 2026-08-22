# -*- coding: utf-8 -*-
"""x0824 X投稿4本の機械QC: 字数 / 「。」直後改行 / CTA・署名・タグ"""
import io, os, re

BASE = r"C:\Users\user\oshinavi\tmp\x0824"
CTA = "▼チケット情報はこちら → https://oshinavi.jp"
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'

lines_out = []
for i in range(1, 5):
    path = os.path.join(BASE, f"p{i}.txt")
    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    total_with_nl = len(text)
    count = len(text.replace("\n", ""))  # 字数=改行を除く全文字(URL含む)

    # 「。」の直後が改行か（末尾の。はOK）
    bad_kuten = []
    for m in re.finditer("。", text):
        j = m.end()
        if j < len(text) and text[j] != "\n":
            bad_kuten.append(text[max(0, m.start() - 10):j + 10].replace("\n", "\\n"))
    kuten_ok = (len(bad_kuten) == 0)

    cta_ok = CTA in text
    sign_ok = SIGN in text
    tag_line = text.rstrip("\n").split("\n")[-1]
    tags = re.findall(r"#\S+", tag_line)
    tag_ok = tag_line.startswith("#チケット発売") and len(tags) == 2

    len_ok = 250 <= count <= 330
    lines_out.append(f"p{i}.txt")
    lines_out.append(f"  字数(改行除く・URL込み): {count}  [250-330: {'OK' if len_ok else 'NG'}]  (改行込み全長: {total_with_nl})")
    lines_out.append(f"  「。」直後が全部改行: {'OK' if kuten_ok else 'NG ' + ' / '.join(bad_kuten)}")
    lines_out.append(f"  CTA行あり: {'OK' if cta_ok else 'NG'}")
    lines_out.append(f"  署名行あり: {'OK' if sign_ok else 'NG'}")
    lines_out.append(f"  タグ行({tag_line}): {'OK' if tag_ok else 'NG'}")
    lines_out.append("")

report = "\n".join(lines_out)
with io.open(os.path.join(BASE, "qc.txt"), "w", encoding="utf-8") as f:
    f.write(report)
print(report.encode("unicode_escape").decode("ascii")[:20] and "WROTE")
# ASCIIで要点だけ出す（コンソール文字化け対策）
for i, block in enumerate(range(1, 5)):
    pass
import json
summary = []
for i in range(1, 5):
    path = os.path.join(BASE, f"p{i}.txt")
    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    count = len(text.replace("\n", ""))
    bad = sum(1 for m in re.finditer("。", text) if m.end() < len(text) and text[m.end()] != "\n")
    summary.append({"file": f"p{i}", "chars": count, "len_ok": 250 <= count <= 330,
                    "kuten_bad": bad, "cta": CTA in text, "sign": SIGN in text})
print(json.dumps(summary))
