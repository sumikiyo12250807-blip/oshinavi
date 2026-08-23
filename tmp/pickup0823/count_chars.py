# -*- coding: utf-8 -*-
"""pickup0823 の各txtを機械カウントして qc の素材を出す"""
import io, os, sys

DIR = r"C:\Users\user\oshinavi\tmp\pickup0823"
FILES = ["lede.txt", "exile.txt", "hotei.txt", "magokoro.txt",
         "morningmusume.txt", "kooza.txt", "takashima.txt", "tail.txt"]

out = []
for name in FILES:
    path = os.path.join(DIR, name)
    with io.open(path, "r", encoding="utf-8") as f:
        text = f.read()
    body = text.replace("\r", "").replace("\n", "")  # 改行を除いた実字数
    lines = [ln for ln in text.replace("\r", "").split("\n") if ln != ""]
    line_lens = " / ".join(str(len(ln)) for ln in lines)
    out.append("%s: %d字 (改行除く) / 行別 %s" % (name, len(body), line_lens))

result = "\n".join(out)
sys.stdout.buffer.write((result + "\n").encode("utf-8"))
