# -*- coding: utf-8 -*-
"""「大物なのに OSHINAVI に載っていない」を炙り出す。

  python tools/check_big_artists.py tmp/ltike_hot_0910.json

## なぜ要るか（2026-09-10 ユーザー）

> 「昨日**藤井風が oshinavi.jp に無かった**件ね。大物で、みんなが行きたそうなコンサートは
>  うちにないものがないか、それを探してほしい。**私の職場の人が藤井風のチケットを買うというので
>  私が知ったの**。そんな感じで知ったのね。大物ってどこかから情報とれないかな」

🚨藤井風は **e+の独占**（eplus.jp/fujiikaze-pianorecital/）だった。
  ぴあや楽天のランキングを見ても引っかからない＝**売り場に依存しない一覧**が要る。

## 情報源＝ローチケの「注目」ページ（実ブラウザで読む）

`https://l-tike.com/concert/` に、ローチケが選んだ名前が並んでいる:
  注目チケット／先行受付／**今週末一般発売開始**／発売中・公演間近／注目のアーティスト
🚨ローチケは WebFetch/curl が全滅なので**実ブラウザで開いて画面から読む**
  （[[reference_ltike_machine_unreachable]]）。読んだ結果を JSON に落としてここへ渡す。

## 判定

登録の `artist` と `name` を正規化して**部分一致**で当てる。
🚨部分一致は「新日本フィル」が「日本フィル」に飲まれる型の事故があるので、
  **消す判断には使わない**。ここは「**見に行く手がかりを出すだけ**」なので部分一致でよい。

## 🆕 --window YYYY-MM-DD:YYYY-MM-DD ＝「載っているが枠が足りない」も出す（2026-09-10 追加）

名前が当たっても安心できない。2026-09-10 の実測＝
**GENERATIONS・森高千里・清水ミチコは載っているのに、持っている枠が「先行」だけ**で、
その週に始まる一般発売の枠を1つも持っていなかった。

- `check_zero_badge.js` … 枠が1つでも生きていれば通る（先行が生きているので出ない）
- 名前の突き合わせ … 名前があれば「載っている」で終わる
- `reconcile_pia --new` … 新着プールしか見ない

＝**この層はどのゲートも見ていない**。だから窓を渡したら
「その窓に**発売が始まる枠**（startDate が窓の中）を持っているか」まで見る。
関連: [[feedback_capture_all_deadlines_on_add]]
"""
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　]+', '', s)
    s = re.sub(r'[『』「」【】（）\(\)＜＞<>\[\]［］～〜\-‐−–—・,、.。/／!！?？:：;；"\'”’]', '', s)
    return s.lower()


def starts_in(ev, lo, hi):
    """この窓のあいだに「発売が始まる枠」を持っているか"""
    for t in ev.get('tickets') or []:
        sd = t.get('startDate')
        if sd and lo <= sd <= hi:
            return True
    return False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    win = None
    for a in sys.argv[1:]:
        if a.startswith('--window'):
            win = a.split('=', 1)[1] if '=' in a else None
    if win is None and '--window' in sys.argv:
        i = sys.argv.index('--window')
        if i + 1 < len(sys.argv):
            win = sys.argv[i + 1]
            args = [a for a in args if a != win]
    lo = hi = None
    if win:
        lo, hi = win.split(':')

    src = args[0] if args else 'tmp/ltike_hot_0910.json'
    hot = json.load(open(src, encoding='utf-8'))

    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    events = json.loads(m.group(2))
    hay = []
    for e in events:
        hay.append((norm(e.get('artist')), norm(e.get('name')), e))

    print('=== 大物チェック（%s）===' % src)
    if lo:
        print('    窓 %s 〜 %s に「発売が始まる枠」を持っているかも見る' % (lo, hi))
    missing = []
    gap = []
    for sec, names in hot.items():
        if sec.startswith('_'):
            continue
        print('\n■ %s' % sec)
        for nm in names:
            k = norm(nm)
            if not k:
                continue
            hits = [e for a, n2, e in hay if k and (k in a or k in n2)]
            if hits:
                ids = ','.join(str(e['id']) for e in hits[:4])
                if lo and not any(starts_in(e, lo, hi) for e in hits):
                    print('   ⚠️ %-28s 載っているが**この窓に発売が始まる枠が無い**（id=%s）'
                          % (nm[:28], ids))
                    gap.append((sec, nm, ids))
                else:
                    print('   ✅ %-28s 載っている（%d件 id=%s）' % (nm[:28], len(hits), ids))
            else:
                print('   🚨 %-28s **載っていない**' % nm[:28])
                missing.append((sec, nm))

    print('\n=== 載っていない %d件 ===' % len(missing))
    for sec, nm in missing:
        print('   [%s] %s' % (sec, nm))
    if lo:
        print('\n=== 載っているが、この窓に発売が始まる枠が無い %d件 ===' % len(gap))
        for sec, nm, ids in gap:
            print('   [%s] %-30s id=%s' % (sec, nm[:30], ids))
    with open('tmp/big_artists_missing.txt', 'w', encoding='utf-8') as f:
        f.write('# 大物なのに OSHINAVI に載っていない（%s）\n\n' % src)
        for sec, nm in missing:
            f.write('- [%s] %s\n' % (sec, nm))
    print('→ tmp/big_artists_missing.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
