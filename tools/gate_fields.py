# -*- coding: utf-8 -*-
"""登録の「枠の外」の欄を見る番人。2026-10-09 新設。

  python tools/gate_fields.py          … 全件を見る（exit 0＝健全／1＝要対応）
  python tools/gate_fields.py --ids 1,2

## なぜ要るか（2026-10-09 ユーザー「振り分けの時ゲートくぐっても間違えてるってこと？」）

reconcile_pia・gate_*_slots は「枠が売り場と合っているか」しか見ない。次の3つは**ゲートを通って振り分けまで届いていた**：

- A 名前の欄（artist/name）に URL が入っている（id27418＝livePocket の出演者欄が YouTube の URL）
- B 会場は1つなのに県が「全国」（23610 華優希＝都市センターホテル／32851 起雲閣／ぴあ「海外」の韓国公演）
- C カードの日付（ev.date）が、枠に書いた最後の公演日より前＝**千秋楽より前に画面から消える**
  （郷ひろみ・アンダーグラフ・HY など53件。足し込みで後日の公演が増えても date を伸ばしていなかった／
    TIGET はカードの日付が受付の日になっていた8件）

## 決まり
- B の除外＝配信・全国の上映劇場・WEB受験・全国の店舗で使える券（TBC 9271〜9273）
- C は「最後の公演日が今日以降」だけ数える（もう終わった組は画面に関係しない）
- 直し方の雛形＝tmp/x1009/fix_fields.py（A/B）・fix_c.py（C）・fix_tiget_dates.py（TIGET）
"""
import datetime, io, json, re, sys

ROOT = 'C:/Users/user/oshinavi/'
B_OK = {9271, 9272, 9273}  # TBC＝全国の店舗で使える券
PAT = re.compile(r'（[^（）]*?(R9年\s*)?(\d{1,2})/(\d{1,2})(?:[〜・](R9年\s*)?(\d{1,2})/(\d{1,2}))?公演）')


def main():
    today = datetime.date.today().isoformat()
    s = io.open(ROOT + 'index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    if '--ids' in sys.argv:
        ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')}
        E = [e for e in E if e['id'] in ids]
    A, B, C = [], [], []
    for e in E:
        nm = (e.get('artist') or '') + ' ' + (e.get('name') or '')
        if re.search(r'https?://|www\.|\.(jp|com|net)/', nm):
            A.append(e)
        v = e.get('venue') or ''
        prefs = {m.group(1) for t in e.get('tickets') or [] for m in [re.search(r'（([^（）\s]+?)\s', t.get('type') or '')] if m}
        if (e.get('prefecture') == '全国' and prefs and prefs <= {'全国'} and e['id'] not in B_OK
                and not re.search(r'STREAM|配信|上映劇場|SPWN|WEB|docomo|Zaiko Live|★', v + (e.get('name') or '') + (e.get('dateLabel') or ''))):
            B.append(e)
        last = None
        for t in e.get('tickets') or []:
            mm = PAT.search(t.get('type') or '')
            if not mm:
                continue
            if mm.group(5):
                y = 2027 if (mm.group(4) or mm.group(1)) else 2026
                d = '%d-%02d-%02d' % (y, int(mm.group(5)), int(mm.group(6)))
            else:
                d = '%d-%02d-%02d' % (2027 if mm.group(1) else 2026, int(mm.group(2)), int(mm.group(3)))
            last = max(last or d, d)
        if last and last >= today and e.get('date') and e['date'] < last:
            C.append((e, last))
    print(f'=== gate_fields (today={today}) 対象{len(E)}件 ===')
    for e in A:
        print(f'  A id{e["id"]} 名前の欄にURL: {(e.get("artist") or "")[:60]}')
    for e in B:
        print(f'  B id{e["id"]} 会場1つで県が全国: {(e.get("name") or "")[:30]} ｜{(e.get("venue") or "")[:30]}')
    for e, last in C:
        print(f'  C id{e["id"]} date={e["date"]} < 最後の公演 {last}: {(e.get("name") or "")[:30]}')
    print(f'=== 集計: A {len(A)} / B {len(B)} / C {len(C)} ===')
    sys.exit(1 if (A or B or C) else 0)


if __name__ == '__main__':
    main()
