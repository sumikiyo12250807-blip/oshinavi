import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/tmp/x0928e/'
sel = json.load(open(R + 'sc_sel.json', encoding='utf-8'))
def page(slug):
    L = open(R + 'sc_txt/' + slug + '.txt', encoding='utf-8').read().split('\n')
    a = L.index('概要', L.index('ログアウト'))
    b = L.index('販売元', a) if '販売元' in L[a:a+60] else a + 12
    info = [x for x in L[a+1:b] if not x.startswith('〒') and 'マップ' not in x]
    d = info[info.index('開催日') + 1] if '開催日' in info else None
    ven = info[info.index('会場') + 1] if '会場' in info else None
    t = info[info.index('時間') + 1: info.index('会場')] if '時間' in info and '会場' in info else []
    c = max(i for i, x in enumerate(L) if x == '受付・チケット情報')
    e = L.index('同じ会場のイベントを検索', c)
    rec = []
    for i in range(c, e):
        if L[i] == '販売受付期間':
            st = L[i-3] if L[i-3] != 'ファンクラブチケット' else L[i-4]
            rec.append({'status': st, 'kind': L[i-2], 'name': L[i-1], 'start': L[i+1], 'end': L[i+2].lstrip('〜')})
    m = re.match(r'(.*) \((.+?[都道府県])\)$', ven or '')
    return {'url': 'https://livepocket.jp/e/' + slug, 'dates': d, 'time': t, 'venue': m.group(1) if m else ven, 'pref': m.group(2) if m else None, 'receptions': rec}
ERR = {
 '24635': [{'url': 'https://livepocket.jp/e/nl3yl', 'item': '【飲食・２名席】9/29 の状態', 'truth': '予定販売枚数終了（soldout）', 'registered': 'soldout なし（販売中扱い）', 'kind': '状態の遅れ（登録後に売り切れ）'}],
 '24877': [{'url': 'https://livepocket.jp/e/olc23', 'item': '畳んだ会期のページ', 'truth': '10/26（月）心斎橋BIGSTEP店のページ olc23 がある（販売中・主催者ページ /p/v96ok に掲載）', 'registered': '10/26 の枠なし（10ページ中 10/26 だけ抜け）', 'kind': '収集か畳みの穴（日付別ページの取りこぼし）'}],
 'b23': [{'url': 'https://livepocket.jp/e/cluemetic-popup_ebisu', 'item': '受付の数', 'truth': '先着販売受付×4（予定販売枚数終了1・販売中3・同名同締切）', 'registered': '1枠（soldoutなし）', 'kind': 'ビルダーの穴（同名同締切の受付を畳む）'}],
 'b462': [{'url': 'https://livepocket.jp/e/do6ch', 'item': '受付の数', 'truth': '先着販売受付×3（予定販売枚数終了2・販売中1・同名同締切）', 'registered': '2枠（soldout1・販売中1）', 'kind': 'ビルダーの穴（同名同締切の受付を畳む）'}],
 'b96': [{'url': 'https://livepocket.jp/e/rbnhz', 'item': '受付の数', 'truth': '先着販売受付×3（販売前・VIP/一般/U-25で受付が別・同名同日時）', 'registered': '1枠', 'kind': 'ビルダーの穴（同名同締切の受付を畳む）'}],
}
NOTE = {'24979': '開催日は12/14と12/22の2日だけ（別ページ）。dateLabel「12月14日〜12月22日」は会期に見える（初日・最終日は一致するので誤りには数えない）'}
out = []
for s in sel:
    e = s['entry']
    urls = []
    for u in [e['links']['livepocket']] + [t.get('url') for t in e.get('tickets', [])]:
        if u and u not in urls: urls.append(u)
    out.append({'src': 'index.html' if s['src'] == 'IDX' else 'built', 'key': s['key'], 'name': e.get('name'),
                'pages': [page(u.rstrip('/').split('/e/')[1]) for u in urls],
                'errors': ERR.get(s['key'], []), 'note': NOTE.get(s['key'])})
json.dump({'checkedAt': '2026-09-28 20:30頃（生HTMLは tmp/x0928e/sc_html/）', 'entries': out}, open(R + 'lp_truth_30.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ids = [s['key'] for s in sel if s['src'] == 'IDX']
open(R + 'sc_ids.txt', 'w').write(','.join(ids))
json.dump({'entries': [s['entry'] for s in sel if s['src'] == 'BLT']}, open(R + 'sc_built13.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), sum(len(o['errors']) for o in out), ','.join(ids))
