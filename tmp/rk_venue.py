import sys, re
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

body = R.fetch('https://ticket.rakuten.co.jp/music/fes/rtax026/')
i = body.find('会場')
while i > 0:
    seg = body[i - 200: i + 600]
    if 'performance' in seg or 'venue' in seg.lower():
        print('--- 生HTML ---')
        print(seg.replace('\n', ' ')[:900])
        print()
        break
    i = body.find('会場', i + 1)

# 会場 : の直後のタグ構造
for m in list(re.finditer(r'会場\s*[:：]\s*', body))[:3]:
    print('>>>', body[m.end(): m.end() + 300].replace('\n', ' '))
    print()
