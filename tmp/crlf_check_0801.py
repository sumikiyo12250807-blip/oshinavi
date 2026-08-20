import io, sys

p = r"C:\Users\user\oshinavi\index.html"
b = open(p, "rb").read()
crlf = b.count(b"\r\n")
lf = b.count(b"\n")
stray = lf - crlf
print("CRLF=%d  LF_total=%d  stray_LF=%d" % (crlf, lf, stray))
if stray:
    # 位置を数行だけ報告
    idx = 0
    shown = 0
    while shown < 10:
        i = b.find(b"\n", idx)
        if i < 0:
            break
        if i == 0 or b[i-1:i] != b"\r":
            line = b[:i].count(b"\n") + 1
            print("  stray LF at line", line)
            shown += 1
        idx = i + 1
