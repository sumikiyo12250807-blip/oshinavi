# -*- coding: utf-8 -*-
"""git push の前に、今日すでに何回 push したかを数え、3回に達していたら止める（2026-09-27 ユーザー決定）。

きっかけ＝9/27 に1日26回 push した（決まりは1日3回・朝昼晩＝memory feedback_push）。
数え方＝`git reflog show refs/remotes/origin/main` の「update by push」のうち今日の日付の行。
4回目がどうしても要る時＝ユーザーに理由を言ってOKをもらい、
  .claude/state/push_extra_ok_YYYYMMDD.txt に許可する回数（例: 4）を書く。その回数までは通す。
"""
import datetime
import json
import os
import re
import subprocess
import sys

LIMIT = 3
ROOT = r'C:/Users/user/oshinavi'


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode('utf-8', 'replace') or '{}')
    except Exception:
        return 0
    cmd = ((data.get('tool_input') or {}).get('command') or '')
    # 実行される git push だけを見る＝行頭か ; & | ( の直後に来る「git [-C 道] push」。
    # 文章の中の「`git push` を止める」などには反応しない（2026-09-27 誤検知で直した）。
    if not re.search(r'(?:^|[;&|(]|\bthen\b|\bdo\b)\s*git\s+(?:-C\s+\S+\s+)?push\b', cmd, re.M):
        return 0
    today = datetime.date.today().strftime('%m-%d')
    try:
        out = subprocess.run(['git', '-C', ROOT, 'reflog', 'show', 'refs/remotes/origin/main',
                              '--date=format:%m-%d %H:%M'], capture_output=True, timeout=20).stdout.decode('utf-8', 'replace')
    except Exception:
        return 0
    n = sum(1 for ln in out.splitlines() if ('{%s ' % today) in ln and 'update by push' in ln)
    limit = LIMIT
    ok = os.path.join(ROOT, '.claude', 'state', 'push_extra_ok_%s.txt' % datetime.date.today().strftime('%Y%m%d'))
    if os.path.exists(ok):
        try:
            limit = max(limit, int(open(ok, encoding='utf-8').read().strip() or LIMIT))
        except Exception:
            pass
    if n >= limit:
        sys.stderr.buffer.write((
            'BLOCKED: 今日はもう %d 回 push しています（上限 %d 回＝朝・昼・夜の便の最後に1回ずつ／memory: feedback_push）。\n'
            '途中の直しは commit だけにして、次の便の締めでまとめて押すこと。\n'
            'どうしても今押す必要があるなら、理由をユーザーに伝えてOKをもらい、'
            '.claude/state/push_extra_ok_%s.txt に許可された回数を書いてから押す。\n'
            % (n, limit, datetime.date.today().strftime('%Y%m%d'))).encode('utf-8'))
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
