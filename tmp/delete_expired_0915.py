# -*- coding: utf-8 -*-
"""公演が終わったエントリを index.html から消す（2026-09-15 朝の便）。delete_expired_0914.py の日付違い。

DELETE_GATE.md の手順どおり：
  ・別エージェントの独立検証（「削除は誤りという前提で」・候補値は見せていない）で「消してよい」だった分だけ
  ・配信・視聴券の語がある子は機械で見送る（要目視）
  ・URLは index.html から機械抽出する（手で書かない）

使い方: python tmp/delete_expired_0915.py <id,id,...> [--apply]
"""
import argparse
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today()
# 配信の語があるが、エージェントが配信券も販売終了と確かめた id（今日は無し）
ALLOW = set()
KEPT_NOTE = ('残したもの＝5019 田中れいな・8351 Chevon（続きの公演が売り切れで未登録＝足すか消すかをユーザーに聞いている）／'
             '1904・8383（配信で買える枠）／'
             '2416 白酒・一之輔 大手町二人会（配信の視聴券が 9/28 15:45 まで受付中＝ぴあ b2670323・e+ 0507030033-P0030153P021001）／'
             '6907 さにこ会 vol.3（9/30 大阪 YES THEATER 16:30回が e+ 4393340001-P0030003P021001 で受付中）。')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ids')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    IDS = [int(x) for x in args.ids.split(',') if x.strip()]

    src = open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))
    byid = {e['id']: e for e in events}

    rows, ng = [], []
    for i in IDS:
        e = byid.get(i)
        if not e:
            ng.append((i, 'エントリが無い'))
            continue
        if (e.get('date') or '9999') >= TODAY.isoformat():
            ng.append((i, '公演日が今日以降 date=%s' % e.get('date')))
            continue
        hay = (e.get('dateLabel') or '') + ' ' + ' '.join(t.get('type', '') for t in (e.get('tickets') or []))
        if i not in ALLOW and re.search(r'(配信|視聴|アーカイブ|ライブビューイング)', hay):
            ng.append((i, '配信/視聴の語がある＝要目視'))
            continue
        ls = e.get('links') or {}
        url = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        if not url:
            url = next((t.get('url') for t in (e.get('tickets') or []) if t.get('url')), '')
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
    open(bak, 'w', encoding='utf-8', newline='').write(src)
    nl = '\r\n' if '\r\n' in src else '\n'
    arr = json.dumps(left, ensure_ascii=False, indent=2).replace('\n', nl)
    out = src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():]
    # 新着の並び(NEW_ORDER)に消した id があれば外す
    mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
    if mo:
        order = [int(x) for x in mo.group(1).split(',') if x.strip()]
        order2 = [x for x in order if x not in kill]
        if order2 != order:
            out = out[:mo.start()] + 'const NEW_ORDER = [%s];' % ', '.join(str(x) for x in order2) + out[mo.end():]
    open('index.html', 'w', encoding='utf-8', newline='').write(out)

    log = 'logs/removed_%s.md' % TODAY.isoformat()
    with open(log, 'a', encoding='utf-8') as f:
        f.write('\n## 公演が終わったため（%d件）\n\n' % len(rows))
        f.write('別エージェントの独立検証（「削除は誤りという前提で」・今日の scratchpad/delcheck_0915）で「消してよい」だった分。\n')
        f.write(KEPT_NOTE + '\n\n')
        f.write('| id | 公演名 | 公演日 | 会場 | 確認用URL |\n|---|---|---|---|---|\n')
        for i, n, d, v, u in rows:
            f.write('| %s | %s | %s | %s | %s |\n' % (i, n.replace('|', '／'), d, v.replace('|', '／'), u))
    print('%d件を削除（backup: %s ／ 記録: %s ／ 残り %d件）' % (len(rows), bak, log, len(left)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
