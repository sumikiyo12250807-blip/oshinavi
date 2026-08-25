# id=1006 神戸新開地・喜楽館 の date を 2026-08-23 → 2026-08-30 に直す
# （8/30夜席の枠が生きているのに千秋楽が古いまま＝データ誤り）
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()

m = re.search(r'"id":\s*1006\s*,', s)
assert m, 'id=1006 が見つからない'
start = m.start()
# エントリブロックの終端を探す
i = s.rfind('{', 0, start)
depth = 0
for j in range(i, len(s)):
    if s[j] == '{': depth += 1
    elif s[j] == '}':
        depth -= 1
        if depth == 0: break
block = s[i:j+1]

assert block.count('"date": "2026-08-23"') == 1, block.count('"date": "2026-08-23"')
newblock = block.replace('"date": "2026-08-23"', '"date": "2026-08-30"')
s2 = s[:i] + newblock + s[j+1:]
assert len(s2) == len(s)

io.open(path, 'w', encoding='utf-8', newline='').write(s2)
print('id=1006 の date を 2026-08-30 に修正した')
print('CRLF:', s2.count('\r\n'), ' bare LF:', len(re.findall(r'(?<!\r)\n', s2)), ' CRCRLF:', s2.count('\r\r\n'))
