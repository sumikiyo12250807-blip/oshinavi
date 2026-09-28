"""gate_badge_render.py — 画面のバッジ（日付・時刻・ラベル）を実際の表示コードで確かめる番人の呼び出し役

Why（2026-09-28 夜 ユーザー指摘）: id24621 グレープカンパニーで、データは正しいのに画面が
「本日発売 〜10/25 21:00」（締切の日付に発売時刻）と出ていた。データのゲートは全部通っていた
＝表示コード（index.html の renderCard）が出した文字そのものを見る。中身は tools/gate_badge_render.js。

やること:
  1. index.html を一時フォルダへコピーしてから使う（ヒール中に書き換わっても壊れない／index.html は読むだけ）
     --rev <commit> を付けると `git show <commit>:index.html` を書き出して使う（直す前の再現用）
  2. node tools/gate_badge_render.js をコピーに対して流す（--today は , 区切りで何日でも）
  3. 報告 tmp/gate_badge_render_report.txt ＋ 標準出力に1日1行
     「カード◯件・枠◯・A違反◯・B◯・C◯・描画失敗◯」。1つでも違反があれば exit 1

使い方:
  python tools/gate_badge_render.py                                  # 今日・00:00 と 23:59 の2時点
  python tools/gate_badge_render.py --today 2026-09-28,2026-09-29,2026-10-05
  python tools/gate_badge_render.py --rev 25d4bfab^ --today 2026-09-28   # 直す前で鳴るかの確認
  オプション: --time 00:00,23:59 / --report パス / --append / --label 名前
"""
import argparse
import datetime
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    ap.add_argument('--rev', default=None, help='git の版を使う（例 25d4bfab^）')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--time', default='00:00,23:59')
    ap.add_argument('--report', default=os.path.join(ROOT, 'tmp', 'gate_badge_render_report.txt'))
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--label', default='')
    a = ap.parse_args()

    tmpd = tempfile.mkdtemp(prefix='gate_badge_')
    try:
        copy = os.path.join(tmpd, 'index.html')
        if a.rev:
            data = subprocess.run(['git', 'show', f'{a.rev}:index.html'], cwd=ROOT,
                                  capture_output=True, check=True).stdout
            with open(copy, 'wb') as f:
                f.write(data)
            label = a.label or f'版 {a.rev}'
        else:
            shutil.copyfile(a.html, copy)
            label = a.label or '現在の index.html'
        cmd = ['node', '--max-old-space-size=4096', os.path.join(ROOT, 'tools', 'gate_badge_render.js'),
               '--html', copy, '--today', a.today, '--time', a.time,
               '--report', a.report, '--label', label]
        if a.append:
            cmd.append('--append')
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode not in (0, 1):
            print(f'番人そのものが失敗（exit {r.returncode}）', file=sys.stderr)
            return 2
        return r.returncode
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
