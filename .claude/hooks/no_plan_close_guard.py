# -*- coding: utf-8 -*-
"""Stop hook: 「段取り・予告・承認待ち」の文でターンを閉じようとしたら1回だけ止める番人。

memory: feedback_selfrun_gates_only_two（2026-09-16・09-17 に同じ型を3回）
  ユーザー「プッシュまで未承認でお任せしてるけど、どうしてまた忘れちゃったのよ　ちゃんと読んで」（9/16）
  ユーザー「朝・昼・夜のプッシュまで自走で未承認でお願いしてる　ちゃんと読んで　そして、二度とこの間違いを繰り返さない対処をして」（9/17）
型＝裏のジョブ待ちで「〜が終わったら〜の順に進めるわね」「押すわね」と書いてターンを閉じる
  ＝承認を待っているように読める。push・削除・ぴあの振り分けは承認不要（検証が通ったらその場でやって「やった」と報告）。

見るのは「直近のユーザー発言以降で最後の assistant テキスト」だけ（締めの文）。
同じ発話で2回は止めない（state/plan_close_seen.txt）。番人自体が壊れても作業は止めない（exit 0）。
"""
import json, os, re, sys, glob

PATTERNS = [
    r'(押す|プッシュする|pushする|push する)わ(ね|よ)?',
    r'(終わったら|済んだら|通ったら|終わり次第|済み次第|のあとで?|その後).{0,80}(進める|やる|押す|回す|入る|移る|片付ける)わ(ね|よ)?[。\s]*$',
    r'(順に|順番で)進めるわ(ね|よ)?',
    r'(OKなら|よければ|いいかしら|していい[？?]|してよい[？?]|押していい|プッシュしていい)',
    r'(承認|GO|合図)(を)?待',
]


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 🆕2026-10-02 ユーザー「プッシュまだ？って言わなきゃプッシュしないわけじゃないよね？　自走わすれてないよね？
#   もし忘れてるなら、二度と自走を忘れないようにするシステムを作って」
#   型＝朝の便の中身（削除・ヒール・振り分け・新着）を直し終えたのに、裏の新着集め1本を「待つわね」で待ち続けて
#   朝のpushを止めた（8時すぎ）。この番人は「押すわね」は止めても「待つわね」は素通りだった。
WAIT_PAT = r'(待つわ|待っている|待ってる|待ちね|終わるのを待|終わり次第|が終わったら|が終わるまで)'
MORNING_PUSH_BY = (9, 30)   # 朝のpushの締め時刻＝これを過ぎて今日まだ1回も押していなければ、文に関係なく止める


def _git(*args):
    import subprocess
    try:
        r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True, text=True, encoding='utf-8', timeout=20)
        return r.stdout.strip()
    except Exception:
        return ''


def morning_push_pending():
    """今日まだ1回も push していない（origin/main の先端が今日でない）のに、未pushの commit がある"""
    import datetime as dt
    now = dt.datetime.now()
    unpushed = [x for x in _git('log', '--oneline', 'origin/main..HEAD').splitlines() if x.strip()]
    if not unpushed:
        return None
    tip = _git('log', '-1', '--format=%cI', 'origin/main')
    try:
        tip_d = dt.datetime.fromisoformat(tip).date()
    except Exception:
        return None
    if tip_d >= now.date():
        return None
    return now, len(unpushed)


def push_wait_check(uuid, tail, state):
    """朝の便：①6〜12時に「待つ」で閉じる ②9:30を過ぎても今日のpushが0回 ＝ どちらも止める（それぞれ1回ずつ）"""
    st = morning_push_pending()
    if not st:
        return 0
    now, n = st
    if not (6 <= now.hour < 12):
        return 0
    key = None
    if (now.hour, now.minute) >= MORNING_PUSH_BY:
        key = 'mpush_late_' + now.strftime('%Y%m%d')
        why = '🚨 %s を過ぎたのに、今日の朝のpushがまだ（未push %d本）。' % ('%d:%02d' % MORNING_PUSH_BY, n)
    elif re.search(WAIT_PAT, tail):
        key = 'mpush_wait_' + uuid
        why = '🚨 朝のpushがまだ（未push %d本）なのに、裏のジョブを「待つ」でターンを閉じようとしている。' % n
    if not key:
        return 0
    seen_f = os.path.join(state, 'plan_close_seen.txt')
    seen = open(seen_f, encoding='utf-8').read().split() if os.path.exists(seen_f) else []
    if key in seen:
        return 0
    with open(seen_f, 'w', encoding='utf-8') as f:
        f.write('\n'.join((seen + [key])[-200:]))
    sys.stderr.write(
        why + '（2026-10-02 ユーザー「プッシュまだ？って言わなきゃプッシュしないわけじゃないよね？」）\n'
        '朝のpushは「直し終えた成果をいちばん早く出す」ため（feedback_morning_routine）。'
        '裏で時間のかかる収集（livePocket・TIGET など）が1本残っているだけなら、それを待たずに '
        'fold_parts --check → gate_badge_render → build_ai_page → reconcile_pia --new → compact_events --apply → commit → push を今やる。'
        '残りの収集は昼の便のpushに乗せる（迷った件・終わっていない件は省いて押す＝feedback_selfrun_gates_only_two）。'
        '押したら「押した」とだけ報告。\n')
    return 2


def main():
    try:
        data = json.loads(sys.stdin.read() or '{}')
    except Exception:
        data = {}
    if data.get('stop_hook_active'):
        return 0
    tp = data.get('transcript_path') or ''
    d = os.path.dirname(tp) if tp and os.path.exists(tp) else os.path.join(
        os.path.expanduser('~'), '.claude', 'projects', re.sub(r'[:\\/]', '-', data.get('cwd') or os.getcwd()))
    files = sorted(glob.glob(os.path.join(d, '*.jsonl')), key=os.path.getmtime, reverse=True)
    if not files:
        return 0
    with open(files[0], encoding='utf-8') as f:
        lines = f.readlines()
    last = None
    for ln in reversed(lines):
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') == 'user':
            c = (o.get('message') or {}).get('content')
            if isinstance(c, list) and any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c):
                continue
            break
        if o.get('type') != 'assistant':
            continue
        c = (o.get('message') or {}).get('content')
        texts = [c] if isinstance(c, str) else [b.get('text') for b in (c or []) if isinstance(b, dict) and b.get('type') == 'text' and b.get('text')]
        if texts:
            last = (str(o.get('uuid')), '\n'.join(texts))
            break
    if not last:
        return 0
    uuid, text = last
    tail = text.strip()[-400:]
    state = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'state')
    os.makedirs(state, exist_ok=True)
    rc = push_wait_check(uuid, tail, state)
    if rc:
        return rc
    hits = [p for p in PATTERNS if re.search(p, tail, re.M)]
    if not hits:
        return 0
    # ❓付きの相談（ユーザーが決める方針の質問）は止めない。ただし push・削除・振り分けの許可を聞いている時は止める（2026-09-17 誤作動2回目）
    if '❓' in tail and not re.search(r'(push|プッシュ|押し|削除|消し|振り分け)', tail):
        return 0
    # 🆕2026-09-27 pushは1日3回まで＝「commit済み・次の便（朝/昼/夜・明朝）で押す」は正しい締め方＝止めない
    #   （この見張りを避けようとして直すたびに押し、1日26回になった）
    if re.search(r'(commit|コミット)', tail) and re.search(r'(次の便|朝の便|昼の便|夜の便|明朝|明日の朝)', tail):
        return 0
    # X投稿の文面は「ユーザーが見てから予約」が正しいゲート（X_SCRIPT.md ⛔）＝その確認では止めない（2026-09-17 誤作動）
    if re.search(r'予約', tail) and re.search(r'(投稿|文面|本文|ピックアップ)', text):
        return 0
    state = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'state')
    os.makedirs(state, exist_ok=True)
    seen_f = os.path.join(state, 'plan_close_seen.txt')
    seen = open(seen_f, encoding='utf-8').read().split() if os.path.exists(seen_f) else []
    if uuid in seen:
        return 0
    with open(seen_f, 'w', encoding='utf-8') as f:
        f.write('\n'.join((seen + [uuid])[-200:]))
    sys.stderr.write(
        'BLOCKED: 段取り・予告・承認待ちに読める文でターンを閉じようとしている（memory: feedback_selfrun_gates_only_two）。'
        '🚨pushは1日3回まで（朝・昼・夜の便の最後に1回ずつ）＝便の途中の直しは commit だけ（2026-09-27 に26回押した）。'
        'push・削除・ぴあの振り分けは承認不要＝検証が通ったら許可を待たずにやって「やった」と報告する（pushは便の締めで）。'
        '「〜したら押すわね」「〜の順に進めるわね」で閉じない。いま着手できる作業（ぴあを使わない点検・plan.md・memory・次の便の素材）に手を付けてから、やったことだけを報告して。\n')
    return 2


if __name__ == '__main__':
    try:
        sys.stderr.reconfigure(encoding='utf-8')  # Windows の既定 cp932 だと表示が化ける
    except Exception:
        pass
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
