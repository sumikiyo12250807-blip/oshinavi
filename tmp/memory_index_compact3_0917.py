import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory\MEMORY.md'
lines = open(P, encoding='utf-8').read().split('\n')
NEW = {
11: '- 🚨 [pushの前にこの便でやると決めたことが全部終わったか数える](feedback_push_after_assign.md)／🚨🚨 [pushは1日3回・朝昼夜とも**承認不要**](feedback_push.md)（検証が通ったら**その場で押して「押した」と報告**・**「押すわね」「〜したら〜進めるわね」で閉じない**＝Stopフック no_plan_close_guard.py）／[便の締めに未pushをgitで確認](feedback_unpushed_commit_check.md)／[Netlifyクレジット](project_netlify_credits.md)',
47: '- 🚨 [全部の本文にURLを貼る](feedback_x_no_link_spam.md)／[誘導先は必ずoshinavi.jp](feedback_x_link_oshinavi_only.md)／🚨[CTAは「▼チケット情報はこちら」固定＋URLで着地先を絞る](feedback_x_cta_wording.md)（主役`?q=名前`／まとめ`?genre=&status=urgent`）／[外部リンク抑制記事](reference_x_external_link_article.md)',
94: '- [ツアー・複数会場は1エントリ](feedback_tour_consolidate.md)／[長期公演も1エントリ](feedback_longrun_event.md)／🚨[各ticketに会場別pia URL](feedback_tour_per_ticket_url.md)（畳む前にurl空の枠へ飛び先を焼き込む）／[ツアー検証は全URL開いて再導出](feedback_bundle_full_rederive.md)',
29: '- [自走停止の真因は複合コマンドのexpansion確認](feedback_no_expansion_commands.md)／[許可プロンプト・パイプ先未許可](reference_autonomy_permission_allowlist.md)／🚨[コマンドの説明は日本語](feedback_confirm_before_run.md)（サブエージェントにも「descriptionは日本語で」と指示）',
59: '- 🎨 [宣材の「oshinavi.jp」は光る白](feedback_x_image_url_white_glow.md)／🎬[「お毒姐さん」動画を1日1本](project_odoku_x_video.md)（🚨声も構図も参照画像で決まる＝言葉でなく画で与える）／[MiniMax APIキーのローテ](reference_minimax_key_rotation.md)',
54: '- 🎯 [投稿ごとの実測を貯める](project_x_post_analytics.md)／📏[数字の測り方と生きている観察](feedback_x_ctr_observations.md)（2〜4日で伸びる／展示は主役にしない／RTが起点）／🔥[夜の便の最初にトレンド×在庫](feedback_x_trend_match_inventory.md)',
33: '- 🚨🚨 [公演日は「事実の会期」で書く＝買える範囲に縮めない](feedback_show_true_dates_not_sellable_range.md)（入れるのはこれから行われる公演だけ／始まっている展覧会・長い公演は本当の初日から）',
87: '- 🚨🚨 [ヒールは券種違いを丸ごと消す＝走らせたらHEADと枠数を突合](feedback_heal_flattens_ticket_types.md)（安全弁の分は**足し算**・売り切れ枠は残す）／🚨🚨[「カードは出るのに買える枠0」の番人＝毎朝`check_zero_badge.js`](feedback_zero_badge_gate.md)',
}
before = len('\n'.join(lines))
for n, s in NEW.items():
    key = s.split('](')[1].split(')')[0]
    assert key in lines[n - 1], (n, key)
    lines[n - 1] = s
txt = '\n'.join(lines)
open(P, 'w', encoding='utf-8', newline='').write(txt)
print('文字数', before, '→', len(txt))
