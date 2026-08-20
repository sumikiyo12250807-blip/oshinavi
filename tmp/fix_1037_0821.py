# -*- coding: utf-8 -*-
"""1037 おどる絵本『みえるとか みえないとか』を削除候補から救い出す。

check_expired は「公演終了(8/20)・全販売終了」で削除候補に挙げたが、
独立検証で **水戸芸術館ACM劇場 9/5(土)15:00・9/6(日)10:30・9/6(日)14:00 の3公演が残っている**
ことが分かった。しかも**ぴあにもe+にも無く、主催（水戸芸術館）だけが売っている**。
＝「大手に無い＝公演が無い」で消してはいけない型（[[feedback_delete_nonpia_blindspot]]）。

出典（実アクセス確認済）:
  https://www.arttowermito.or.jp/theatre/lineup/article_4324.html
    → 9/5(土)15:00 ／ 9/6(日)10:30 ／ 9/6(日)14:00・ACM劇場・一般発売2026年6月6日9:30〜
      完売/受付終了の表示なし・購入は窓口/電話(029-225-3555)/WEB(e-get)
  https://www.saf.or.jp/stages/detail/107249/ （ツアー全日程・企画制作＝彩の国さいたま芸術劇場）

🚨**販売終了日はページに明記が無い**ので、チケット枠は今回入れない（推測日付は禁止
[[feedback_unknown_end_date]]／[[feedback_no_placeholder_dates]]）。ユーザーに扱いを相談する。
ここでは事実として確認できた 公演日・会場・県・公式リンク だけを直す。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 1037:
        continue
    print('before date=%s venue=%s pref=%s' % (e['date'], e['venue'], e['prefecture']))
    e['date'] = '2026-09-06'
    e['dateLabel'] = '2026年8月16日(日)〜2026年9月6日(日) 兵庫・神奈川・茨城'
    e['venue'] = '全国ツアー（神戸文化ホール 中ホール／茅ヶ崎市民文化会館 大ホール／水戸芸術館 ACM劇場）'
    e['prefecture'] = '兵庫・神奈川・茨城'
    links = e.get('links') or {}
    links['official'] = 'https://www.arttowermito.or.jp/theatre/lineup/article_4324.html'
    e['links'] = links
    e['verifiedAt'] = '2026-08-21'
    print('after  date=%s venue=%s pref=%s' % (e['date'], e['venue'], e['prefecture']))
    n += 1

assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_1037')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
