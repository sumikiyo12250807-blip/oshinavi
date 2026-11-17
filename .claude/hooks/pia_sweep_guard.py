# -*- coding: utf-8 -*-
"""git push の前に「ぴあの見直し（tools/pia_soldout_sweep.py）」が回ったかを確かめ、回っていなければ止める。

きっかけ＝2026-11-17 抜き打ち 46001 梅棒『eatBeat』：登録のあとにぴあへ足された
「ポスター付き当日引換券」（〜11/29 10:00・受付中）がカードに無かった。reconcile_pia --ids では MISSING と出る＝
道具は拾えるのに、登録済みを毎日見る「ぴあの見直し」が 11/11 を最後に6日間回っていなかった
（logs/pia_sweep_2026-11-12〜17 が無い）。止まっても何も鳴らなかったのが真因。

決まり（memory feedback_pia_soldout_sweep_3days）＝毎日・昼の便のあと〜17時に回す。
- 夜の push（17時以降）＝今日の logs/pia_sweep_<今日>.md に中身が無ければ止める
- 朝の push（17時より前）＝昨日の logs/pia_sweep_<昨日>.md に中身が無ければ止める
どうしても回せなかった日＝理由をすちこに伝えたうえで
  .claude/state/pia_sweep_skip_YYYYMMDD.txt に理由を書く（その日の分だけ通す）。
"""
import datetime
import json
import os
import re
import sys

ROOT = r'C:/Users/user/oshinavi'


def has_log(d):
    p = os.path.join(ROOT, 'logs', 'pia_sweep_%s.md' % d.strftime('%Y-%m-%d'))
    try:
        return os.path.getsize(p) > 200
    except OSError:
        return False


def skipped(d):
    return os.path.exists(os.path.join(ROOT, '.claude', 'state', 'pia_sweep_skip_%s.txt' % d.strftime('%Y%m%d')))


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode('utf-8', 'replace') or '{}')
    except Exception:
        return 0
    cmd = ((data.get('tool_input') or {}).get('command') or '')
    if not re.search(r'(?:^|[;&|(]|\bthen\b|\bdo\b)\s*git\s+(?:-C\s+\S+\s+)?push\b', cmd, re.M):
        return 0
    now = datetime.datetime.now()
    d = now.date() if now.hour >= 17 else now.date() - datetime.timedelta(days=1)
    if has_log(d) or skipped(d):
        return 0
    sys.stderr.buffer.write((
        'BLOCKED: %s の「ぴあの見直し」（tools/pia_soldout_sweep.py）が回っていません（logs/pia_sweep_%s.md が無い・空）。\n'
        '登録したあとでぴあに足された受付・売り切れを拾うのはこの道具だけ＝止まると抜けが溜まる（11/17 梅棒の当日引換券）。\n'
        '直し方：python tools/pia_soldout_sweep.py --apply（--resume で続きから）→ 取りこぼしを heal --ids → commit → push。\n'
        'どうしても回せない時は、すちこに理由を伝えてから .claude/state/pia_sweep_skip_%s.txt に理由を書く。\n'
        % (d.strftime('%m/%d'), d.strftime('%Y-%m-%d'), d.strftime('%Y%m%d'))).encode('utf-8'))
    return 2


if __name__ == '__main__':
    sys.exit(main())
