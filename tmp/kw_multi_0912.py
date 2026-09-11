# -*- coding: utf-8 -*-
"""ぴあのキーワード検索を名前ごとに順番に回して、結果を1ファイルにまとめる（読むだけ）。
pia_kw_search.py は出力先が固定なので並列に回さない（上書きし合う）。
使い方: python tmp/kw_multi_0912.py 名前1 名前2 ...
出力: tmp/kw_multi_0912.txt
"""
import io
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
out = io.open('tmp/kw_multi_0912.txt', 'w', encoding='utf-8')
for name in sys.argv[1:]:
    r = subprocess.run([sys.executable, 'tools/pia_kw_search.py', name],
                       capture_output=True, env={'PYTHONIOENCODING': 'utf-8', **__import__('os').environ})
    txt = (r.stdout or b'').decode('utf-8', 'replace') + (r.stderr or b'').decode('utf-8', 'replace')
    out.write('===== %s (rc=%s) =====\n%s\n' % (name, r.returncode, txt))
    out.flush()
    time.sleep(4)
out.close()
print('終わったわ → tmp/kw_multi_0912.txt')
