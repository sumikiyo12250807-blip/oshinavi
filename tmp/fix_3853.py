# -*- coding: utf-8 -*-
"""id3853 阪神タイガース対広島東洋カープ（9/17 甲子園）の枠を戻す。

昼のヒールが 12枠 → 1枠 に潰した。ぴあの実ページを1枚ずつ読んだところ、
消えた11枠は**すべて `予定枚数終了`**（今日9/1 12:00発売→即日完売）だった。
売り切れは消さずに「予定枚数終了」で表示し続ける決まり
（memory: feedback_soldout_keep_visible）なので、`soldout` を付けて戻す。

残す1枠＝「ビジター専用応援席」はぴあで受付中（〜9/17 14:00）。ヒールが入れた
締切のほうが正しいので、現物をそのまま使う。

🚨index.html は newline='' で読み書きして改行を壊さない。
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-01'

# ぴあの実ページで「予定枚数終了」を確認した券種（2026-09-01 実測・tmp/hanshin_statustext.txt）
SOLDOUT_CONFIRMED = {
    'アルプス楽楽シート／一般発売（兵庫 9/17公演）9/1 12:00発売',
    '一般発売（兵庫 9/17公演）9/1 12:00発売',
    '見切り席／一般発売（兵庫 9/17公演）9/1 12:00発売',
    '一般発売【車椅子席】（兵庫 9/17公演）9/1 12:00発売',
    '一般発売【DTSボックス】（兵庫 9/17公演）9/1 12:00発売',
    '限定企画チケット発売【「ドコモラウンジ」付きチケット】（兵庫 9/17公演）9/1 12:00発売',
    '一般発売【三ツ矢サイダーボックス】（兵庫 9/17公演）9/1 12:00発売',
    '限定企画チケット発売【NTTドコモビジネスファミリーシート引換券】（兵庫 9/17公演）9/1 12:00発売',
    '限定企画チケット発売【JCBエキサイトシート】（兵庫 9/17公演）9/1 12:00発売',
    '一般発売【セコム ツイン・トリプルシート】（兵庫 9/17公演）9/1 12:00発売',
    '一般発売【パナソニックペアシート】（兵庫 9/17公演）9/1 12:00発売',
}
KEEP_NOW = 'ビジター専用応援席／一般発売（兵庫 9/17公演）〜9/17 14:00'


def dumps_tickets(tickets):
    """index.html の tickets ブロックと同じ体裁（インデント6/8・CRLF）で吐く。"""
    lines = ['    "tickets": [\r\n']
    for i, t in enumerate(tickets):
        lines.append('      {\r\n')
        keys = [k for k in ('type', 'date', 'startDate', 'url', 'soldout', 'soldoutSince') if k in t]
        for j, k in enumerate(keys):
            v = json.dumps(t[k], ensure_ascii=False)
            lines.append('        "%s": %s%s\r\n' % (k, v, '' if j == len(keys) - 1 else ','))
        lines.append('      }%s\r\n' % ('' if i == len(tickets) - 1 else ','))
    lines.append('    ],\r\n')
    return ''.join(lines)


def main():
    head = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8')
    HE = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', head, re.S).group(1))}
    old = HE[3853]['tickets']

    s = io.open(P, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', s, re.S)
    cur = {e['id']: e for e in json.loads(m.group(2))}
    now = cur[3853]['tickets']
    assert len(now) == 1 and now[0]['type'] == KEEP_NOW, now

    new = [now[0]]
    missing = []
    for t in old:
        # ビジター専用応援席はヒールが「9/1 12:00発売」→「〜9/17 14:00」に書き換えた同じ枠。
        # 現物側（KEEP_NOW）を使うので、HEAD 側のこの枠は読み飛ばす。
        if t['type'].startswith('ビジター専用応援席／一般発売（兵庫 9/17公演）'):
            continue
        if t['type'] in SOLDOUT_CONFIRMED:
            t = dict(t)
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            new.append(t)
        else:
            missing.append(t['type'])
    print('戻す枠 =', len(new) - 1, ' / 販売中で残す =', 1)
    if missing:
        print('!! 実ページで確認できていない券種があるので中止:', missing)
        return 1

    # 現物の tickets ブロックを差し替える（id3853 のブロックだけ）
    i = s.find('"id": 3853,')
    j = s.find('    "tickets": [\r\n', i)
    k = s.find('    ],\r\n', j) + len('    ],\r\n')
    print('置換範囲 OK' if 0 < j < k else '!! 範囲が取れない')
    s2 = s[:j] + dumps_tickets(new) + s[k:]

    io.open('index.html.bak_0901_fix3853', 'w', encoding='utf-8', newline='').write(s)
    io.open(P, 'w', encoding='utf-8', newline='').write(s2)
    b = open(P, 'rb').read()
    print('CRLF=%d bare_LF=%d CRCRLF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n'), b.count(b'\r\r\n')))
    # 検算
    chk = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', io.open(P, encoding='utf-8').read(), re.S).group(1))
    for e in chk:
        if e['id'] == 3853:
            print('適用後 tickets =', len(e['tickets']), ' soldout =', sum(1 for t in e['tickets'] if t.get('soldout')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
