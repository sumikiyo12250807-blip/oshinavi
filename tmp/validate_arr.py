import re, json

for path in ('index.html', 'events.html'):
    html = open(path, encoding='utf-8').read()
    m = re.search(r'(?:const|var|let)\s+(\w+)\s*=\s*\[', html)
    if not m:
        print(path, "no array decl")
        continue
    idx = m.end() - 1  # at '['
    depth = 0
    i = idx
    end = None
    instr = False
    esc = False
    while i < len(html):
        c = html[i]
        if instr:
            if esc:
                esc = False
            elif c == '\\':
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        i += 1
    arr = html[idx:end]
    try:
        data = json.loads(arr)
        print(path, m.group(1), "OK entries =", len(data))
    except Exception as e:
        print(path, "PARSE FAIL:", e)
        mm = re.search(r'char (\d+)', str(e))
        if mm:
            c = int(mm.group(1))
            print("  ctx:", repr(arr[max(0, c-100):c+100]))
