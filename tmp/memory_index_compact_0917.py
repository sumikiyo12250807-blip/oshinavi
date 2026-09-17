import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory\MEMORY.md'
lines = open(P, encoding='utf-8').read().split('\n')
NEW = {
121: '- [HTML機械パースで新着構築＝build_pia_entries](reference_pia_tickets_tool.md)（🚨is-beforeのまま「中止/延期/販売を終了致しました/お取り扱いしておりません/販売を見合わせ」が出る＝文言で弾く）／🚨[reconcile_pia.py／MISSINGの「受付中」を鵜呑みにしない](reference_reconcile_pia_tool.md)／[QCゲートも鉄壁でない](reference_reconcile_pia_qc_gate.md)／🚨🚨[叩きすぎるとQCゲートが静かに壊れる](reference_pia_rate_limit_429.md)（FETCH＝照合できなかった／**大きい照合は同時に2本回さない**）',
72: '- 🚨🚨 [**登録済みエントリに、ぴあが後から足した会場・先行が入らない**](feedback_existing_entries_miss_new_windows.md)＝X素材の前に明日〜3日後発売をぴあ一覧と突き合わせ／文面を見せる前に全アーティスト名でぴあ総ざらい／🚨**「未登録」はeventCdでなく県＋公演日で当てる**',
75: '- 🚨🚨 [重複判定を「名前」でやると巻き添えで消える＝eventCdで](feedback_harvest_name_dedup_blindspot.md)／🚨[育成は`--rls-from all`](feedback_grow_audit_rlsfrom_blindspot.md)／🚨🚨[ツアーのぴあ外取りこぼし＝**会場数の根拠は公式**・WebFetchに公式を要約させない](feedback_tour_cross_channel_blindspot.md)',
124: '- [e+生HTML機械パース](reference_eplus_machine_parse.md)／[eplus_harvest.py](reference_eplus_harvest.md)／[キーワード検索](reference_eplus_keyword_search.md)／🚨[e+削除は登録枠の死だけで決めない](feedback_eplus_delete_blindspot.md)／🚨🚨[ハーベスタの系統バグとQC](project_eplus_harvester_bug_and_qc.md)（**gate_eplus_slotsとreconcile_eplusは2枚とも通す**）',
130: '- 💰 [アフィリエイト提携の現況](reference_affiliate_status.md)（🚨**Amazon適格販売の期限 9/27〜9/28**／自分・家族の購入は規約違反／ぴあは提携拒否→再申請可・楽天チケットは承認済み）／[Amazonアフィリ設定](reference_amazon_affiliate.md)（音源CD無いイベントはボタン付けない）',
126: '- 🚨🚨 [**楽天の入口は2本＝post-sitemap＋特設ページ**](reference_rakuten_harvest.md)（lastmodで絞らない）／🚨🚨**売り状態はAJAXにしかない**＝`tools/rakuten_perf_status.py`／🆕[ローチケは実ブラウザなら取れる](reference_ltike_machine_unreachable.md)',
120: '- 🚨🚨 [**掘り切ったのは「発売前」だけ＝ぴあ全体は約55%・受付中が手つかず**](project_pia_presale_caught_up.md)（本気で回せば1日261件／部分一致で畳むと別団体が消える）／[範囲外ページで最終ページを返す](reference_pia_pagination_overrun.md)／[「本日発売」は時刻だけ表記](reference_pia_today_sale_timeonly.md)／[状態はHTMLクラスで判定](feedback_harvest_status_by_class.md)',
12: '- 🗓 [記事は週の頭から仕込む](project_weekly_rhythm_and_morphic.md)／📖[週1の読み物「今週のピックアップ」](project_weekly_pickup_article.md)（🚨導入文は読者の場面＋アーティストが何をするか）／🚨[記事は出す前にファクトチェック](feedback_article_factcheck_before_publish.md)',
77: '- 🚨[新着追加時に買える枠を1つ残らず展開](feedback_capture_all_deadlines_on_add.md)（🚨突き合わせは券種名でなく「県・公演日・締切」）／[複数販売スケジュールは全部展開](feedback_tickets_all_expand.md)／[先行が複数公演対象か確認](feedback_presale_scope_per_show.md)',
}
before = len('\n'.join(lines))
for n, s in NEW.items():
    old = lines[n - 1]
    key = s.split('](')[1].split(')')[0]
    assert key in old, (n, key)
    lines[n - 1] = s
txt = '\n'.join(lines)
open(P, 'w', encoding='utf-8', newline='').write(txt)
print('文字数', before, '→', len(txt))
