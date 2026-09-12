# -*- coding: utf-8 -*-
"""ぴあのまとめページ（eventBundleCd）から中の公演（eventCd）を拾い、各公演の状態テキストを生HTMLのまま書き出す（読むだけ）。
tools/pia_statustext.py は eventCd しか受けないので、その前段。
使い方: python tmp/statustext_bundle_0912.py <出力.txt> <bundleCd> [<bundleCd> ...]
"""
import io
import re
import sys
import time

sys.path.insert(0, 'tools')
from build_pia_entries import fetch          # noqa: E402
from pia_statustext import statuses          # noqa: E402

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
out_path, bundles = sys.argv[1], sys.argv[2:]
buf = []
for b in bundles:
    burl = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=%s' % b
    buf.append('■■ %s' % burl)
    try:
        bh = fetch(burl)
    except Exception as e:
        buf.append('   まとめページが取れなかった: %s: %s' % (e.__class__.__name__, e))
        continue
    cds = sorted(set(re.findall(r'eventCd=(\d+)', bh)))
    buf.append('   中の公演 eventCd: %s' % ' '.join(cds))
    for txt, cls, around in statuses(bh):
        buf.append('   (まとめページ上) [%s] %s …%s' % (txt, cls, around[-160:]))
    for cd in cds:
        time.sleep(1.2)
        url = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % cd
        buf.append('  ■ %s' % url)
        try:
            h = fetch(url)
        except Exception as e:
            buf.append('     取得できなかった: %s: %s' % (e.__class__.__name__, e))
            continue
        st = statuses(h)
        if not st:
            buf.append('     状態テキストが1つも無い')
        for txt, cls, around in st:
            buf.append('     [%s] %s' % (txt, cls))
            buf.append('          …%s' % around[-200:])
io.open(out_path, 'w', encoding='utf-8').write('\n'.join(buf) + '\n')
print('wrote %s (%d lines)' % (out_path, len(buf)))
