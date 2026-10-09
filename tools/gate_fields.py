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

## 🆕2026-10-09 夜 抜き打ち30件（ズレ19件）の原因から足した型
- D FANY の公演名が「・・・」で切れている（19789）＝原因はビルダーが公演の name（長いと切られる）を使っていた
  → build_fany_entries.full_name()（event.name＋sub_name）に直した。番人は FANY のリンクを持つ件だけ見る
- F 会場が「設定中」「調整中」のまま（livePocket 31526）
- H 発売日を過ぎたのに締切が無い枠が画面に出ている（ぴあ 29203 ほか45枠）＝ヒール漏れ。画面に出る枠（date＞＝今日）だけ数える
- （livePocket の「1受付＝1枠」で入場券の売り切れ・2部が消えた型はビルダー側で直した＝券種ごとに1枠）
- （全角数字は売り場自身の表記なので数えない＝直しても毎日の見直しで戻る）

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
    sys.stdout.reconfigure(encoding='utf-8')
    today = datetime.date.today().isoformat()
    s = io.open(ROOT + 'index.html', encoding='utf-8').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    if '--ids' in sys.argv:
        ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',')}
        E = [e for e in E if e['id'] in ids]
    A, B, C, D, F, G, H = [], [], [], [], [], [], []
    for e in E:
        # D 公演名・出演者が途中で切れている（FANY の一覧は長い名前を「・・・」で切る＝19789）
        for k in ('name', 'artist'):
            if re.search(r'(・・・|…)\s*$', e.get(k) or '') and (e.get('links') or {}).get('fany'):
                D.append((e, k))
        # F 会場が決まっていない言葉のまま（livePocket「設定中」＝31526）
        if re.fullmatch(r'\s*(設定中|調整中)\s*', e.get('venue') or ''):
            F.append(e)
        # G 全角数字が名前・券種に残っている（[[feedback_newpool_fullwidth_halfwidth]]・18817「１３時３０分」）
        # （全角数字は売り場自身の表記＝FANY「１３時３０分」。直しても毎日の見直しで売り場の表記に戻る＝番人には入れない）
        # H 発売日を過ぎたのに締切が無い枠（「M/D HH:MM発売」で止まっている＝ヒール漏れ・29203）
        for t in e.get('tickets') or []:
            ty = t.get('type') or ''
            if (re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売$', ty) and not t.get('soldout')
                    and t.get('startDate') and t['startDate'] < today and (t.get('date') or '') >= today):
                H.append((e, ty))
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
    for e, k in D:
        print(f'  D id{e["id"]} {k}が途中で切れている: {(e.get(k) or "")[:60]}')
    for e in F:
        print(f'  F id{e["id"]} 会場が「{e.get("venue")}」のまま: {(e.get("name") or "")[:30]}')
    for e in G:
        print(f'  G id{e["id"]} 全角数字: {(e.get("name") or "")[:40]}')
    for e, ty in H:
        print(f'  H id{e["id"]} 発売日を過ぎたのに締切なし: {ty[:60]} ｜{(e.get("name") or "")[:24]}')
    print(f'=== 集計: A {len(A)} / B {len(B)} / C {len(C)} / D {len(D)} / F {len(F)} / G {len(G)} / H {len(H)} ===')
    sys.exit(1 if (A or B or C or D or F or H) else 0)


if __name__ == '__main__':
    main()
