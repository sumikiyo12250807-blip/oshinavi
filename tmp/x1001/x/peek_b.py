import re, sys
sys.stdout.reconfigure(encoding="utf-8")
t = open("index.html", encoding="utf-8").read()
for i in sys.argv[1].split(","):
    m = re.search(r'id\D{0,4}' + i + r'\b', t)
    if not m:
        print(i, "NOTFOUND"); continue
    s = t[m.start():m.start() + 900]
    s = re.sub(r'"tickets".*', '', s, flags=re.S)
    print(i, s.replace("\n", " ")[:600]); print("---")
