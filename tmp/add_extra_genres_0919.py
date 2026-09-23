# ユーザー指示（9/19夜）＝怪談のイベントに「怪談」を足す（元のジャンルはそのまま＝extraGenres）／アイドルのいる生活に「アイドル」
# 名前で怪談だと言い切れるものだけ。文字が当たっただけ（呪術廻戦・オペラ座の怪人・DQ呪われし姫君・都市伝説・謎解き 等）は外した
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
KAIDAN = [5539, 6148, 7542, 8598, 9403, 11336, 11342, 11354, 11374, 11375, 11376, 11415, 11575, 11689, 11726,
          11980, 11981, 12084, 12085, 12220, 12262, 12332, 12347, 12415, 12828, 12840, 12854, 12904, 12982,
          13137, 13160, 13161, 13983, 14991, 16308]
IDOL = [11359]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
n = 0
for e in events:
    for ids, g in ((KAIDAN, 'kaidan'), (IDOL, 'idol')):
        if e['id'] in ids and e.get('genre') != g:
            ex = e.get('extraGenres') or []
            if g not in ex:
                e['extraGenres'] = ex + [g]
                n += 1
                print('＋%s id%d %s' % (g, e['id'], (e.get('name') or '')[:40]))
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('足した', n)
