import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory\MEMORY.md'
lines = open(P, encoding='utf-8').read().split('\n')
NEW = {
121: '- [build_pia_entries](reference_pia_tickets_tool.md)（🚨is-beforeでも「中止/延期/販売を終了致しました/お取り扱いしておりません/販売を見合わせ」は弾く）／🚨[reconcile_pia.py＝MISSINGの受付中を鵜呑みにしない](reference_reconcile_pia_tool.md)／[QCゲートも鉄壁でない](reference_reconcile_pia_qc_gate.md)／🚨🚨[叩きすぎ429](reference_pia_rate_limit_429.md)（FETCH＝照合できなかった／**大きい照合は同時に2本回さない**）',
120: '- 🚨🚨 [**掘り切ったのは発売前だけ＝受付中が手つかず**](project_pia_presale_caught_up.md)（1日261件回せる）／[範囲外ページで最終ページを返す](reference_pia_pagination_overrun.md)／[「本日発売」は時刻だけ](reference_pia_today_sale_timeonly.md)／[状態はHTMLクラスで判定](feedback_harvest_status_by_class.md)',
27: '- 🚨🚨 [止まるのは禁止＝迷った件だけ保留にして手は動かし続ける](feedback_selfrun_gates_only_two.md) — 質問を出す→その件だけ保留→別の作業へ→pushは省いて実行→聞き続ける／🚨**背景ジョブ中も次の作業へ・段取り文でターンを閉じない**',
111: '- [バッジ公演日は完全M/D形](feedback_badge_date_full_form.md)／[2027公演はR9年表記](feedback_r9_year_notation.md)／[同会場同日の時間違いは公演時間](feedback_same_day_show_time_badge.md)／[ツアーのバッジは販売日で分ける](feedback_tour_badge_split_by_saledate.md)／[セレクターは.filter-btn](feedback_filter_selector.md)',
}
before = len('\n'.join(lines))
for n, s in NEW.items():
    key = s.split('](')[1].split(')')[0]
    assert key in lines[n - 1], (n, key)
    lines[n - 1] = s
txt = '\n'.join(lines)
open(P, 'w', encoding='utf-8', newline='').write(txt)
print('文字数', before, '→', len(txt))
