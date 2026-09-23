import re, sys, html, pathlib
for p in sys.argv[1:]:
    b = pathlib.Path(p).read_bytes()
    for enc in ("utf-8", "cp932"):
        try:
            t = b.decode(enc); break
        except UnicodeDecodeError:
            continue
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>|</dd>|</dt>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = "\n".join(l.strip() for l in t.splitlines() if l.strip())
    pathlib.Path(p + ".txt").write_text(t, encoding="utf-8")
    print(p, len(t))
