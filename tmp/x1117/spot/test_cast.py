# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
sys.argv = ['x', 'none.json']
import importlib.util
spec = importlib.util.spec_from_file_location('b', 'C:/Users/user/oshinavi/tools/build_pia_entries.py')
src = open('C:/Users/user/oshinavi/tools/build_pia_entries.py', encoding='utf-8').read()
src = src.split("\nif __name__ == '__main__':")[0] if "\nif __name__ == '__main__':" in src else src[:src.index('cands = json.load(open(sys.argv[1]')]
ns = {'__name__': 'b', '__file__': 'C:/Users/user/oshinavi/tools/build_pia_entries.py'}
exec(compile(src, 'b', 'exec'), ns)
for h in ['<dt>出演者など</dt><dd>［出演］CONNY ／ THE WANDERERS ［オープニングアクト］Ｇｏ　Ｇｏ　Ｍａｒｃｈａｎｓ</dd>',
          '<dt>出演者など</dt><dd>［出場］高原裕之（千里馬神戸） ／ 小坂駿（ＳＵＮ－ＲＩＳＥ） ほか</dd>',
          '<dt>出演者など</dt><dd>［作］井上ひさし ［演出］ふじたあさや ［出演］中西和久</dd>']:
    print(ns['pia_cast'](h))
