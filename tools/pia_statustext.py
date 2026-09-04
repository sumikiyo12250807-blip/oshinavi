# -*- coding: utf-8 -*-
"""ぴあの生HTMLから、券種ごとの状態テキストをそのまま抜き出す。

🚨 `pia_tickets.py` は「予定枚数終了」も「販売終了」も **"受付終了" に潰す**ので、
   売り切れなのか販売期間が終わったのかが分からない。DELETE_GATE 1. の打ち分けにはこれが要る。
     予定枚数終了（売り切れた）→ soldout:true ＋ バッジ「予定枚数終了」（実線）
     販売終了（期間が終わった）→ soldout:true ＋ saleEnded:true ＋ バッジ「販売終了」（点線）
   どちらも**消さない**（[[feedback_soldout_keep_visible]] / [[feedback_saleended_vs_soldout]]）。

使い方:
  python tools/pia_statustext.py <eventCd> [<eventCd> ...]       # 状態テキストを一覧
  python tools/pia_statustext.py --out tmp/x.txt <eventCd> ...   # 出力先を指定

出力は必ずファイルに書く（端末の cp932 で日本語が化けるため＝[[feedback_no_mojibake_japanese_read]]）。
2026-09-05 に `tmp/statustext_0905.py` から昇格。
"""
import re
import io
import sys
import time

sys.path.insert(0, 'tools')
from build_pia_entries import fetch          # noqa: E402  sorry.pia 検出つきの fetch を使う

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def statuses(html):
    """(状態テキスト, CSSクラス, 直前1400文字の地の文) を出現順に返す。"""
    out = []
    for m in re.finditer(r'__status\s+(is-[\w-]+)"[^>]*>(.*?)(?:<br|</p>|</span>)', html, re.S):
        cls, txt = m.group(1), re.sub(r'<[^>]+>', '', m.group(2))
        txt = re.sub(r'\s+', ' ', txt).strip()
        around = re.sub(r'<[^>]+>', ' ', html[max(0, m.start() - 1400):m.start()])
        out.append((txt, cls, re.sub(r'\s+', ' ', around)))
    return out


def main():
    args = sys.argv[1:]
    out_path = 'tmp/pia_statustext.txt'
    if args and args[0] == '--out':
        out_path = args[1]
        args = args[2:]
    if not args:
        print(__doc__)
        return 1

    buf = []
    for cd in args:
        url = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % cd
        buf.append('■ %s' % url)
        try:
            h = fetch(url)
        except Exception as e:
            buf.append('   取得できなかった: %s: %s' % (e.__class__.__name__, e))
            buf.append('')
            continue
        for txt, cls, around in statuses(h):
            buf.append('   [%s] %s' % (txt, cls))
            buf.append('        …%s' % around[-160:])
        buf.append('')
        time.sleep(1.2)

    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(buf) + '\n')
    print('wrote %s (%d lines)' % (out_path, len(buf)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
