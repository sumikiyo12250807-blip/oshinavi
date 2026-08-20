import re

def remove_ids(path, ids, id_indent):
    lines = open(path, encoding='utf-8').read().split('\n')
    removed = []
    # find id line indices
    targets = []
    pat = re.compile(r'^(\s*)"id":\s*(\d+)\s*,')
    for i, l in enumerate(lines):
        m = pat.match(l)
        if m and int(m.group(2)) in ids:
            targets.append((i, int(m.group(2))))
    # process from bottom to top
    for i, eid in sorted(targets, reverse=True):
        # walk back to opening brace line: nearest previous line whose strip()=='{'
        start = i
        while start >= 0 and lines[start].strip() != '{':
            start -= 1
        open_indent = len(lines[start]) - len(lines[start].lstrip())
        # walk forward from i to closing brace at same indent: line strip in ('}', '},')
        end = i
        while end < len(lines):
            s = lines[end].strip()
            ind = len(lines[end]) - len(lines[end].lstrip())
            if s in ('}', '},') and ind == open_indent and end > start:
                break
            end += 1
        del lines[start:end+1]
        removed.append(eid)
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    return removed

idx = remove_ids('index.html', {202,371,408,653,778,861,868,869}, 4)
ev = remove_ids('events.html', {120}, 12)
print('index removed:', sorted(idx))
print('events removed:', sorted(ev))
