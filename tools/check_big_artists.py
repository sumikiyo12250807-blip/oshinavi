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


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'tmp/ltike_hot_0910.json'
    hot = json.load(open(src, encoding='utf-8'))

    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    events = json.loads(m.group(2))
    hay = []
    for e in events:
        hay.append((norm(e.get('artist')), norm(e.get('name')), e))

    print('=== 大物チェック（%s）===' % src)
    missing = []
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
                print('   ✅ %-28s 載っている（%d件 id=%s）' % (nm[:28], len(hits), ids))
            else:
                print('   🚨 %-28s **載っていない**' % nm[:28])
                missing.append((sec, nm))

    print('\n=== 載っていない %d件 ===' % len(missing))
    for sec, nm in missing:
        print('   [%s] %s' % (sec, nm))
    with open('tmp/big_artists_missing.txt', 'w', encoding='utf-8') as f:
        f.write('# 大物なのに OSHINAVI に載っていない（%s）\n\n' % src)
        for sec, nm in missing:
            f.write('- [%s] %s\n' % (sec, nm))
    print('→ tmp/big_artists_missing.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
