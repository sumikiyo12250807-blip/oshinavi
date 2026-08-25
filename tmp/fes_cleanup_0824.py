# -*- coding: utf-8 -*-
"""fes に紛れ込んでいた「フェスでないもの」を正しいジャンルへ移す（2026-08-24）。

きっかけ＝ぴあの「音楽その他」が下書きで fes に落ちる作りだったこと（同日に build_pia_entries を修正）。
OSHINAVI の fes の定義は **複数組＋屋外**（feedback_fes_definition）。屋内ホール・ライブハウスの
単独公演やシネマコンサート、食のイベントは fes ではない。

判断が割れる2件（2270/4527 の二重登録・4361 豊橋 炎の祭典）は**触らない**＝ユーザーに確認中。

使い方: python tmp/fes_cleanup_0824.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
PATH = 'index.html'

FIX = {
    # 食のイベント → gourmet（先例＝3926 ビアフェス／4260 サケマルシェ／4787 ぎょうざ祭り）
    3395: ('gourmet', '酒まつり 酒ひろば＝食のイベント'),
    3396: ('gourmet', '酒まつり 美酒鍋＝食のイベント'),
    3673: ('gourmet', '金沢おいも万博＝食のイベント'),
    3685: ('gourmet', '秋酒祭 愛知＝食のイベント'),
    1509: ('gourmet', 'DElicious BUns FESTIVAL＝食のイベント'),
    # シネマコンサート（屋内ホール・オーケストラ生演奏）→ classic
    3121: ('classic', '「バック・トゥ・ザ・フューチャー」in コンサート＝東京国際フォーラム・屋内'),
    3135: ('classic', 'INTERSTELLAR LIVE＝神戸国際会館/人見記念講堂・屋内'),
    # 屋内（ライブハウス・ホール・展示場）＝fesの「屋外」条件を満たさない → jpop
    1647: ('jpop', '息っ子クラブ 40周年＝四谷Honey Burst・屋内'),
    2742: ('jpop', 'Almirzinho serra＝中目黒トライ・屋内'),
    817: ('jpop', "SKAViLLE JAPAN 2026＝CLUB CITTA'・屋内"),
    1643: ('jpop', 'BAYSIDE CLASH 2026＝横浜ベイホール・屋内'),
    484: ('jpop', '新しい学校のリーダーズ ほか＝インテックス大阪・屋内'),
    # 和太鼓の大会（屋内ホール）→ dento
    1633: ('dento', '太鼓祭in滋賀＝大津市民会館 大ホール・和太鼓'),
    # 韓国のグループのファンコン → kpop
    3153: ('kpop', 'BAE173 FAN-CON＝韓国のグループ'),
}


def main():
    src = io.open(PATH, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in src else '\n'
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    n = 0
    log = io.open('logs/fes_cleanup_2026-08-24.md', 'w', encoding='utf-8')
    log.write('# fes の棚卸し 2026-08-24\n\n')
    log.write('ぴあの「音楽その他」が下書きで fes に落ちる作りだったため、フェスでないものが混ざっていた。\n')
    log.write('OSHINAVI の fes は **複数組＋屋外**（feedback_fes_definition）。\n')
    log.write('同日に `build_pia_entries.py` の落とし先を fes → jpop に直したので、今後は起きない。\n\n')
    log.write('| id | 公演名 | fes → | 理由 | 確認URL |\n|---|---|---|---|---|\n')
    for e in events:
        if e['id'] not in FIX:
            continue
        g, why = FIX[e['id']]
        if e.get('genre') != 'fes':
            print('!! id=%d は genre=%s（fesでない）＝触らない' % (e['id'], e.get('genre')))
            continue
        print('id=%-5d fes -> %-8s %s' % (e['id'], g, why))
        log.write('| %d | %s | **%s** | %s | %s |\n' % (
            e['id'], (e.get('artist') or e.get('title') or '')[:44], g, why,
            (e.get('links') or {}).get('pia') or ''))
        if APPLY:
            e['genre'] = g
        n += 1
    log.write('\n## 触らなかったもの（ユーザーに確認中）\n')
    log.write('- **2270 / 4527 ONE PARK HANGOUT FES2026 in OYABE** … 同じ日・同じ会場の二重登録（表記ゆれ）。畳んでよいか確認中\n')
    log.write('- **4361 第31回 豊橋 炎の祭典** … 手筒花火の祭り。hanabi に移すか fes のままか確認中\n')
    log.close()
    print('\n対象 %d件 → logs/fes_cleanup_2026-08-24.md' % n)

    if not APPLY:
        print('(--apply で書き込み)')
        return 0
    shutil.copyfile(PATH, PATH + '.bak_0824_fescleanup')
    dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
    io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
    print('書き込み完了')
    return 0


if __name__ == '__main__':
    sys.exit(main())
