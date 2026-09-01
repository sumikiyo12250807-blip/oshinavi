# -*- coding: utf-8 -*-
"""ジャンル `dento`（伝統）を、音楽側 `hougaku` と舞台側 `dento` に割る。

ユーザー決定（2026-09-01）＝
  音楽の伝統 = 「演奏を聴きに行くもの」（和太鼓・三味線・琵琶・箏・尺八・雅楽・民謡・邦楽）
  舞台の伝統 = 「演じるのを観に行くもの」（歌舞伎・能・狂言・文楽・日本舞踊・神楽・薪能）

`--apply` を付けない限り一覧を出すだけ。迷った分は動かさずに残す。
🚨index.html は newline='' で読み書きして改行を壊さない
（memory: feedback_index_html_crlf_preserve / feedback_index_html_crcrlf_trap）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
P = 'index.html'

# 「演じるのを観に行く」側＝舞台に残す
STAGE = (r'歌舞伎|能楽|能公演|演能|能の会|薪能|◯能|狂言|文楽|人形浄瑠璃|日本舞踊|舞踊|をどり|踊り|'
         r'神楽|新派|大衆演劇|地芝居|声明|灌頂|寺子屋|玉三郎|萬斎|万作|團十郎|海老蔵|猿之助|勘九郎|'
         r'仁左衛門|菊之助|幸四郎|白鸚|松緑|愛之助|中村屋|松竹|国立劇場 \d+月|古典芸能|伝承ホール')
# 「演奏を聴きに行く」側＝音楽へ移す
MUSIC = (r'和太鼓|太鼓|鼓童|三味線|津軽|琵琶|箏|筝|三曲|尺八|雅楽|民謡|島唄|邦楽|和楽器|篠笛|笛|'
         r'DRUM TAO|吉田兄弟|ジャズ|オーケストラ|コンサート|ライブ|LIVE|演奏会|音楽祭|リサイタル')


def classify(e):
    ps = e.get('_piaSub') or ''
    if '歌舞伎・古典芸能' in ps:
        return 'dento', 'ぴあ=歌舞伎・古典芸能'
    if '邦楽' in ps:
        return 'hougaku', 'ぴあ=邦楽'
    n = ' '.join([e.get('artist') or '', e.get('name') or '', e.get('venue') or '',
                  e.get('dateLabel') or ''])
    hs = bool(re.search(STAGE, n))
    hm = bool(re.search(MUSIC, n))
    if hs and not hm:
        return 'dento', '舞台の語'
    if hm and not hs:
        return 'hougaku', '音楽の語'
    if hs and hm:
        return None, '両方の語（保留）'
    return None, 'どちらの語も無い（保留）'


def main():
    src = io.open(P, encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    evs = json.loads(m.group(2))
    to_h, keep, hold = [], [], []
    for e in evs:
        if e.get('genre') != 'dento':
            continue
        g, why = classify(e)
        row = (e['id'], (e.get('artist') or '')[:50], why)
        if g == 'hougaku':
            to_h.append(row)
        elif g == 'dento':
            keep.append(row)
        else:
            hold.append(row)
    out = []
    out.append('=== dento の割り振り（genre=="dento" のエントリのみ）===')
    out.append('音楽へ移す(hougaku) %d件 / 舞台に残す(dento) %d件 / 保留 %d件'
               % (len(to_h), len(keep), len(hold)))
    out.append('')
    out.append('--- 音楽へ移す %d件 ---' % len(to_h))
    for i, a, w in to_h:
        out.append('  id%-6s %-50s [%s]' % (i, a, w))
    out.append('')
    out.append('--- 保留（動かさない） %d件 ---' % len(hold))
    for i, a, w in hold:
        out.append('  id%-6s %-50s [%s]' % (i, a, w))
    out.append('')
    out.append('--- 舞台に残す %d件 ---' % len(keep))
    for i, a, w in keep:
        out.append('  id%-6s %-50s [%s]' % (i, a, w))
    io.open('tmp/split_dento_0901.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    print('hougaku=%d dento=%d hold=%d  → tmp/split_dento_0901.txt' % (len(to_h), len(keep), len(hold)))

    if not APPLY:
        print('（一覧のみ。適用は --apply）')
        return 0

    ids = {i for i, _, _ in to_h}
    # 1) エントリの genre を書き換える（該当 id の "genre": "dento" だけ）
    def repl(mm):
        body = mm.group(0)
        idm = re.search(r'"id":\s*(\d+)', body)
        if idm and int(idm.group(1)) in ids:
            body = re.sub(r'("genre":\s*)"dento"', r'\1"hougaku"', body, count=1)
        return body
    new_events = re.sub(r'\{\r\n    "id":.*?\r\n  \}', repl, m.group(2), flags=re.S)
    changed = new_events.count('"hougaku"')
    src2 = src[:m.start(2)] + new_events + src[m.end(2):]

    # 2) GENRE_LABEL に追加
    src2 = src2.replace('classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統",',
                        'classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統", hougaku: "伝統",', 1)
    # 3) GENRE_GROUPS.music に追加
    src2 = src2.replace('"chanson","musicetc"],', '"chanson","hougaku","musicetc"],', 1)
    # 4) 音楽グループにボタンを足す（「その他」の前）
    src2 = src2.replace('        <button class="filter-btn" data-genre="musicetc">その他</button>',
                        '        <button class="filter-btn" data-genre="hougaku">伝統</button>\r\n'
                        '        <button class="filter-btn" data-genre="musicetc">その他</button>', 1)

    io.open('index.html.bak_0901_hougaku', 'w', encoding='utf-8', newline='').write(src)
    io.open(P, 'w', encoding='utf-8', newline='').write(src2)
    b = open(P, 'rb').read()
    print('APPLIED genre=%d件  label=%s group=%s button=%s' % (
        changed,
        'hougaku: "伝統"' in src2,
        '"chanson","hougaku","musicetc"' in src2,
        'data-genre="hougaku"' in src2))
    print('CRLF=%d bare_LF=%d CRCRLF=%d' % (b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n'), b.count(b'\r\r\n')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
