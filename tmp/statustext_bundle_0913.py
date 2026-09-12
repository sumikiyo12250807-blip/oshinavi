# -*- coding: utf-8 -*-
"""ぴあの bundle ページ（eventBundleCd=）の券種ごとの状態テキストを抜く。
pia_statustext.py は eventCd 形しか組み立てないので、bundle 用の1回きりの道具。
使い方: python tmp/statustext_bundle_0913.py <eventBundleCd> [...]
出力: tmp/statustext_bundle_0913.txt（端末に日本語を出すと化けるので必ずファイル）
"""
import io
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import fetch  # noqa: E402

out = []
for cd in sys.argv[1:]:
    url = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=%s' % cd
    html = fetch(url)
    out.append('■ %s（%d bytes）' % (url, len(html or '')))
    for m in re.finditer(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', html or '', re.S):
        cls, txt = m.group(1), re.sub(r'<[^>]+>', '', m.group(2)).strip()
        ctx = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', (html[m.end():m.end() + 700])))[:150]
        out.append('   [%s] %s' % (txt, cls))
        out.append('        … %s' % ctx)
    time.sleep(1.5)
io.open('tmp/statustext_bundle_0913.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/statustext_bundle_0913.txt (%d lines)' % len(out))
