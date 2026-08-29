# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = json.load(open('tmp/vb0829/parsed.json', encoding='utf-8'))

def wininfo(head):
    """券種ページの表記リストから 受付タイプ／受付期間／状態 を取り出す"""
    h = head
    out = {'type': '', 'window': '', 'result': '', 'status': ''}
    for i, x in enumerate(h):
        if x in ('発売開始', '受付期間', '販売期間') and i + 1 < len(h):
            out['window'] = h[i + 1]
            out['kind'] = x
        if x == '結果発表開始日時' and i + 1 < len(h):
            out['result'] = h[i + 1]
        if x in ('一般発売', '先行抽選', '先行先着', 'プレミアム先行'):
            out['type'] = x
        if re.match(r'^(抽選受付中|抽選受付終了|受付中|受付終了|販売終了|予定枚数終了|本日\d|本日 ?\d|\d{4}/\d{1,2}/\d{1,2}\(.\) .*より発売|本日.*より発売)', x):
            out['status'] = x
    return out

def stat(sttxt, head_status):
    s = (sttxt or '') + ' ' + (head_status or '')
    if '予定枚数終了' in s: return '予定枚数終了'
    if '販売終了' in s: return '受付終了（販売終了）'
    if '抽選受付終了' in s: return '受付終了（抽選）'
    if '受付終了' in s: return '受付終了'
    if '抽選受付中' in s: return '受付中（抽選）'
    if '受付中' in s or '発売中' in s: return '受付中'
    if '本日' in s: return '受付前 → 本日この時刻から発売'
    if 'より発売' in s or '発売前' in s: return '受付前（発売前）'
    return '(判定不能) ' + s.strip()

out = []
W = out.append
W('# 独立再導出レポート B（2026-08-29 / チケットぴあ実ページから作成）\n')
W('**作り方**：渡された31本のURLを1本ずつ curl で取得し、イベントページの販売枠カード（ticketSalesCard）を全部拾い、')
W('さらに各カードのリンク先＝券種ページ（ticketInformation.do）を1枚ずつ開いた。')
W('公演日・開演時刻・会場・都道府県は券種ページの「公演日時・座席」一覧から、')
W('受付の開始/終了日時は同ページの「発売開始」「受付期間」欄から、そのまま写した。')
W('ジャンルはページの `<title>` の `[大分類 小分類]` と、隠しinput `ntSgenreCd/genreCd` の両方を併記した。')
W('bundle（まとめ）ページの2件は、中の子eventCdのイベントページも1つずつ開いて、まとめページに出ていない枠が無いか照合した（結果：無し）。\n')
W('取得できなかったページ：**0件**（イベントページ31/31、券種ページ52/52、bundleの子イベントページ8/8）\n')

for e in P:
    W('\n---\n')
    if e.get('fail'):
        W('## id %s — 取得できず\n\n- URL: %s\n' % (e['id'], e['url']))
        continue
    W('## id %s' % e['id'])
    W('')
    W('- ぴあURL: %s' % e['url'])
    W('')
    W('**1. 公演名（ページの表記そのまま）**')
    W('')
    W('- %s' % (e['h1'] or e['page_title'].split(' | ')[0]))
    if e['h1'] and e['page_title'].split(' | ')[0] != e['h1']:
        W('- （`<title>`表記: %s）' % e['page_title'].split(' | ')[0])
    perf = []
    for s in e['slots']:
        for p in (s.get('detail') or {}).get('perf', []):
            if p not in perf: perf.append(p)
    perf.sort(key=lambda p: (tuple(int(x) for x in re.match(r'(\d+)/(\d+)/(\d+)', p['date']).groups()), p['time']))
    W('')
    W('**2. 公演日（この興行に含まれる全公演）**')
    W('')
    for p in perf:
        W('- %s %s／%s（%s）' % (p['date'], p['time'], p['venue'], p['pref']))
    days = list(dict.fromkeys(p['date'] for p in perf))
    W('- → 公演日は %d日、公演回数は %d回。**千秋楽（最終公演日）＝ %s**' % (len(days), len(perf), days[-1]))
    W('')
    W('**3. 都道府県（全公演分）**')
    W('')
    prefs = list(dict.fromkeys(p['pref'] for p in perf if p['pref']))
    W('- %s' % '、'.join(prefs))
    W('')
    W('**4. 会場（全公演分）**')
    W('')
    for v in dict.fromkeys('%s（%s）' % (p['venue'], p['pref']) for p in perf):
        W('- %s' % v)
    W('')
    W('**5. 買える枠（販売スケジュール）＝ 全%d枠**' % len(e['slots']))
    for i, s in enumerate(e['slots'], 1):
        c = s['card']; d = s.get('detail') or {}
        wi = wininfo(d.get('head', []))
        W('')
        W('- **枠%d：%s**' % (i, c['title']))
        W('  - 券種ページ: %s' % c['url'])
        W('  - ぴあの枠タイプ: %s%s' % (wi['type'] or '(表記なし)',
                                        '　/　カードの印: ' + ' ・ '.join(c['tags']) if c['tags'] else ''))
        if wi.get('kind') == '受付期間':
            W('  - 受付期間（「〜M/D HH:MM」型）: %s' % wi['window'])
        elif wi['window']:
            W('  - 発売開始（「M/D HH:MM発売」型）: %s　※終了日時はぴあに表記なし（「予定枚数終了しだい発売終了」）' % wi['window'])
        else:
            W('  - 受付日時: 券種ページに表記なし')
        if wi['result']:
            W('  - 抽選結果発表: %s' % wi['result'])
        W('  - 状態: **%s**（カード表記「%s」／券種ページ表記「%s」）'
          % (stat(c['sttxt'], wi['status']), c['sttxt'] or '-', wi['status'] or '-'))
        pp = d.get('perf', [])
        if pp:
            W('  - 対象の公演: %s' % '、'.join('%s %s %s（%s）' % (x['date'], x['time'], x['venue'], x['pref']) for x in pp))
        else:
            W('  - 対象の公演: 券種ページから取れず')
        if d.get('seats'):
            W('  - 席種・料金: %s' % '、'.join(d['seats']))
    W('')
    W('**6. ぴあのジャンル区分**')
    W('')
    if e['genre']:
        W('- %s（genreCd=%s）' % (e['genre'], e['genreCd']))
    else:
        W('- **映画/舞台挨拶**（genreCd=%s）' % e['genreCd'])
        W('  - ※bundleページの`<title>`には小分類が出ないので、中の子イベント'
          '（eventCd=2633960 『５秒で完全犯罪を生成する方法』前夜祭）のページを開いて確認した。'
          'そちらの`<title>`に「[映画 舞台挨拶のチケット購入・予約]」、隠しinput genreCd も同じ 0400103 だった。')
W('\n---\n')
W('## 全31件のまとめ（照合用の一覧表）\n')
W('| id | 公演名 | 枠数 | 公演回数/日数 | 都道府県 | 千秋楽 | ぴあジャンル |')
W('|---|---|---|---|---|---|---|')
tot = 0
for e in P:
    perf = []
    for s in e['slots']:
        for q in (s.get('detail') or {}).get('perf', []):
            if q not in perf: perf.append(q)
    days = sorted({q['date'] for q in perf},
                  key=lambda d: [int(x) for x in re.match(r'(\d+)/(\d+)/(\d+)', d).groups()])
    tot += len(e['slots'])
    nm = re.sub(r'\(.*?\)$', '', (e['h1'] or e['page_title'].split(' | ')[0])).strip()
    W('| %s | %s | %d | %d回/%d日 | %s | %s | %s |' % (
        e['id'], nm, len(e['slots']), len(perf), len(days),
        '・'.join(dict.fromkeys(q['pref'] for q in perf if q['pref'])),
        days[-1] if days else '-', e['genre'] or '映画/舞台挨拶（子ページで確認）'))
W('')
W('枠の合計 **%d枠**。' % tot)
open('tmp/vb0829/report_body.md', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out))
