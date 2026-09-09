# -*- coding: utf-8 -*-
"""公演が終わったエントリを index.html から消す（2026-09-10 朝の便）。

DELETE_GATE.md の手順どおり：
  ・別エージェントの独立検証済み（「削除は誤りという前提で」・候補値は見せていない）
  ・除外リスト（売り切れ／発売時刻前／w.pia直販／他社に生き枠／抽選結果待ち／ぴあだけの照合）は
    今回は「公演が終わった」が理由なので当たらない
  ・配信・視聴券が生きている子は入れない（id1904 は配信が10/4まで生きているので対象外）
  ・URLは index.html から機械抽出する（手で書かない）

使い方: python tmp/delete_expired_0910.py [--apply]
"""
import argparse
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 検証エージェントが「削除してよい」と独立に再導出した18件 ＋ 範囲外で見つかった1件(2866)
IDS = [809, 1052, 1812, 2084, 2728, 2866, 3154, 3765, 4203, 4324, 4941, 4978,
       5577, 5643, 5731, 6187, 6195, 7434, 7466]
TODAY = datetime.date.today()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()

    # 🚨改行の作法＝**読みも書きも既定のまま**（newline を指定しない）。
    #   Windows の text mode は 読み '\r\n'→'\n' ／ 書き '\n'→'\r\n' なので往復で保たれる。
    #   読みだけ newline='' にすると '\r\n' がそのまま入り、書き戻しで '\r\r\n' になる
    #   （2026-09-10 にこれをやって index.html を壊し、gitから戻した）。
    src = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    byid = {e['id']: e for e in events}

    rows, ng = [], []
    for i in IDS:
        e = byid.get(i)
        if not e:
            ng.append((i, 'エントリが無い'))
            continue
        # 安全弁：公演日が今日以降なら消さない
        if (e.get('date') or '9999') >= TODAY.isoformat():
            ng.append((i, '公演日が今日以降 date=%s' % e.get('date')))
            continue
        # 安全弁：券種名やdateLabelに公演日より後の日付が書かれていたら消さない
        hay = (e.get('dateLabel') or '') + ' ' + ' '.join(t.get('type', '') for t in (e.get('tickets') or []))
        if re.search(r'(配信|視聴|アーカイブ|ライブビューイング)', hay):
            ng.append((i, '配信/視聴の語がある＝要目視'))
            continue
        ls = e.get('links') or {}
        url = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        rows.append((i, e.get('name') or '', e.get('date') or '', e.get('venue') or '', url))

    print('消す %d件 / 見送り %d件' % (len(rows), len(ng)))
    for i, why in ng:
        print('  見送り id=%s %s' % (i, why))
    if not args.apply:
        for i, n, d, v, u in rows:
            print('  id=%-5s %s (%s) %s' % (i, n[:44], d, u))
        print('\n（--apply を付けると実際に消す）')
        return 0

    kill = {r[0] for r in rows}
    left = [e for e in events if e['id'] not in kill]
    assert len(events) - len(left) == len(kill), '消える数が合わない'

    bak = 'index.html.bak_%s_del' % TODAY.strftime('%m%d')
    open(bak, 'w', encoding='utf-8').write(src)
    arr = json.dumps(left, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])

    log = 'logs/removed_%s.md' % TODAY.isoformat()
    with open(log, 'w', encoding='utf-8') as f:
        f.write('# %s に消したもの（公演が終わったため）\n\n' % TODAY.isoformat())
        f.write('別エージェントの独立検証（「削除は誤りという前提で」）を通した分。\n')
        f.write('配信・視聴券が生きているものは対象外（id1904 は配信が10/4まで生きているので残した）。\n\n')
        for i, n, d, v, u in rows:
            f.write('- id=%s %s（公演 %s／%s）\n' % (i, n, d, v))
            if u:
                f.write('  - 確認用: %s\n' % u)
    print('%d件を削除（backup: %s ／ 記録: %s ／ 残り %d件）' % (len(rows), bak, log, len(left)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
