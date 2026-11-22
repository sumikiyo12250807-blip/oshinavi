# -*- coding: utf-8 -*-
# Stop フック：5時を過ぎて、その日のアラームを入れた印（.claude/state/alarms_YYYYMMDD.txt）が無ければターンを止める
# 2026-11-22 すちこ「アラームは毎朝かけて、やることやっといてよ」＝早朝の歌詞の合図で始まった日にアラームを1本も入れず 17:30 まで止まった
import datetime, json, os, sys
now = datetime.datetime.now()
if now.hour < 5:
    sys.exit(0)
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
if data.get('stop_hook_active'):
    sys.exit(0)
st = 'C:/Users/user/oshinavi/.claude/state/'
mark = st + 'alarms_%s.txt' % now.strftime('%Y%m%d')
if os.path.exists(mark):
    sys.exit(0)
msg = ('🚨 今日のアラームがまだ入っていません（%s）。\n'
       '   CronCreate（one-shot）で今日の予定を全部入れる＝10:07 記事3本／13:07 抜き打ち30件／昼（最遅の当日発売＋30分・15:30まで）／14:37 X の数字（account_analytics → x_analyze）／16:07 X 準備／18:47 予約／20:47 TikTok／22:07 夜の便＋夜通し／23:43 番人\n'
       '   入れたら CronList で数を確かめ、%s に入れた時刻を書く。\n'
       '   （memory feedback_noon_heal_missed_twice の 11/22 の項）') % (now.strftime('%H:%M'), mark)
sys.stderr.write(msg)
sys.exit(2)
