# -*- coding: utf-8 -*-
"""eplus_harvest.cast_artist の試験（読むだけ）。
2026-09-06 に e+ 実ページの出演者欄を見て手で直した正解（tmp/eplus_artist_rename_0906.py の FIX）と、
同じページから関数が作る名前を突き合わせる。URL は tmp/eplus_artist_src_0906.txt から取る。
🚨 eplus_harvest.py を import すると本体が走るので、関数定義だけを取り出して使う。
使い方: python tmp/test_cast_0912.py
"""
import io
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

code = io.open('tools/eplus_harvest.py', encoding='utf-8').read()
a = code.index('def cast_artist(')
b = code.index('\ndef ', a + 10)
ns = {'re': re}
exec(code[a:b], ns)
cast_artist = ns['cast_artist']

WANT = {
    6951: 'Project U.D.M',
    6956: 'フラワーカンパニーズ／アルカラ／ビレッジマンズストア／LACCO TOWER ほか',
    6962: 'FUNKY MONKEY BΛBY’S',
    6966: '小野大輔／山下大輝／佐藤拓也／櫻井孝宏 ほか',
    6969: 'アロージャズオーケストラ／見砂和照と東京キューバンボーイズ／渡辺真知子',
    6975: 'Hammer Head Shark',
    6978: 'ヒカシュー',
    6934: 'THE BACK HORN／クリープハイプ',
}
src = io.open('tmp/eplus_artist_src_0906.txt', encoding='utf-8').read()
urls = {int(m.group(1)): m.group(2) for m in re.finditer(r'id=(\d+)\n(?:.*\n)*?\s+url\s+:\s+(\S+)', src)}

same = 0
for i, want in WANT.items():
    u = urls.get(i)
    if not u:
        print('id%s URLが見つからない' % i)
        continue
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}),
                                   timeout=40).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('id%s 取得失敗 %s' % (i, ex))
        continue
    got = cast_artist(h)
    ok = (got == want)
    same += ok
    print('%s id%s\n   正解: %s\n   関数: %s' % ('✅' if ok else '❌', i, want, got or '(取れない)'))
    time.sleep(3)
print('\n一致 %d / %d' % (same, len(WANT)))
