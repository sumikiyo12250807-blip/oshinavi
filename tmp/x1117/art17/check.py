import re, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = r"C:\Users\user\oshinavi\tmp\x1117\art17"
NG = re.compile("未就学|歳未満|歳以上有料|手数料|身分証|本人確認|電子チケット|スマチケ|発券|学生証|お支払|クレカ|会員登録|手帳|ぶん|の分|撮影|録音")
W = "月火水木金土日"
for s in ["minamikousetsu", "danseiburanko", "hikawakiyoshi"]:
    t = open(D + "\\" + s + ".md", encoding="utf-8").read()
    lines = t.strip().split("\n")
    body = "".join(lines[5:])
    print(s, "body", len(body), "all", len("".join(lines)))
    for i, l in enumerate(lines, 1):
        if NG.search(l):
            print("  NG", i, NG.search(l).group(0), l)
        if i > 5 and "。" in l[:-1]:
            print("  mid-kuten", i, l)
        yr = 2026
        for m in re.finditer(r"(R9年 )?(\d{1,2})/(\d{1,2})\(([月火水木金土日])", l):
            mo, d, w = int(m.group(2)), int(m.group(3)), m.group(4)
            cands = [y for y in (2026, 2027) if W[datetime.date(y, mo, d).weekday()] == w]
            if not cands:
                print("  WEEKDAY-BAD", i, m.group(0))
            else:
                print("  ok", m.group(0), cands)
