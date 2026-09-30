# -*- coding: utf-8 -*-
"""Bash コマンドが「許可の小窓」を出す書き方なら、実行前に止める（2026-09-30 ユーザー
「小窓出さない約束も見てないの？　何回も同じ間違いしてる　二度と同じ間違いがないようにできないの？」）。

小窓の正体＝式展開・複合コマンドの安全確認（memory: feedback_no_expansion_commands）。
許可リストでは塞げない＝書き方を変えるしかない。7/8・9/28・9/30 と同じ手癖で3回以上出している＝意志では直らないので機械で止める。

止める書き方：
  cd で始める／&& || ; でつなぐ／| でつなぐ／$( ) やバッククォート／<< ヒアドキュメント／for・while ループ／& で裏に回す
代わりに：Write で .py を書いて `python tmp/…/x.py` を1発。裏で回すなら run_in_background を1本ずつ。
リダイレクト（> 出力.txt 2>&1）は止めない。
"""
import json
import re
import sys

RULES = [
    (r'^\s*cd\s', 'cd で始めている（作業ディレクトリは最初から oshinavi）'),
    (r'&&|\|\|', '&& / || でつないでいる'),
    (r';', '; でつないでいる'),
    (r'(?<![>&0-9])\|(?!\|)', '| でつないでいる'),
    (r'\$\(', '$( ) を使っている'),
    (r'`', 'バッククォートを使っている'),
    (r'<<', 'ヒアドキュメント（<<）を使っている'),
    (r'(^|\s)(for|while)\s', 'for / while ループを使っている'),
    (r'(?<![>&0-9])&\s*$|(?<![>&0-9])&\s+(?!1)', '& で裏に回している'),
]


def main():
    try:
        data = json.loads(sys.stdin.buffer.read().decode('utf-8', 'replace') or '{}')
    except Exception:
        return 0
    if (data.get('tool_name') or '') != 'Bash':
        return 0
    cmd = ((data.get('tool_input') or {}).get('command') or '')
    # 引用符の中身（コミットメッセージ等）は見ない＝文字として ; や | が入るのは正当
    bare = re.sub(r'"(?:\\.|[^"\\])*"|\'[^\']*\'', '""', cmd)
    hit = [why for pat, why in RULES if re.search(pat, bare, re.M)]
    if not hit:
        return 0
    sys.stderr.buffer.write((
        'BLOCKED: 許可の小窓が出る書き方です（%s）。memory: feedback_no_expansion_commands／2026-09-30 ユーザー「小窓出さない約束」。\n'
        'Write で .py に書いて `python tmp/…/x.py` を1発で実行すること。裏で回すなら run_in_background を1本ずつ。\n'
        'コマンドは単発だけ（例: python tools/x.py --ids 1,2 > tmp/out.txt 2>&1）。\n' % '・'.join(hit)).encode('utf-8'))
    return 2


if __name__ == '__main__':
    sys.exit(main())
