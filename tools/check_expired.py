#!/usr/bin/env python3
"""期限切れエントリチェック（毎朝のルーチン用・恒久ツール）

【重要】判定ロジックは events.html / index.html の表示ロジックと揃えること。
- events.html: events.html の `getStatus()` (events.html:9343 付近) と同じく endDate を見る
- index.html : tickets[].date が全て今日より前なら販売終了

過去の事故：
- 2026-05-17 朝、endDate を見落とし139件誤判定（本当は16件）→ feedback_check_existing_logic.md

使い方：
  python tools/check_expired.py             # 標準出力に結果
  python tools/check_expired.py --report-file tmp_expired.txt
"""
import argparse
import json
import re
import sys
from datetime import date

DEFAULT_TODAY = date.today()


def extract_events_array(filepath: str):
    """HTML内の `const EVENTS = [ ... ];` を抽出して dict のリストで返す。"""
    with open(filepath, encoding='utf-8') as f:
        text = f.read()
    # 最初の "const EVENTS = [" から、対応する "];" までを抽出
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    if not m:
        raise RuntimeError(f"{filepath}: const EVENTS not found")
    start = m.start(1)
    depth = 0
    end = None
    for i in range(start, len(text)):
        c = text[i]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError(f"{filepath}: array end not found")
    return json.loads(text[start:end])


def is_expired_event(ev: dict, today: date) -> list:
    """events.html 用：endDate（無ければ date）が today より前なら期限切れ。"""
    reasons = []
    end_str = ev.get('endDate') or ev.get('date') or ''
    try:
        end = date.fromisoformat(end_str)
        if end < today:
            reasons.append(f"開催終了{end}")
    except ValueError:
        pass
    return reasons


def is_expired_index(ev: dict, today: date) -> list:
    """index.html 用：全 tickets[].date が today より前なら販売終了。
    （tickets[].date は販売終了日。memory: feedback_ticket_date.md）
    """
    reasons = []
    tickets = ev.get('tickets') or []
    if not tickets:
        return reasons
    all_past = True
    for t in tickets:
        td = t.get('date', '')
        try:
            if date.fromisoformat(td) >= today:
                all_past = False
                break
        except ValueError:
            all_past = False
            break
    if all_past:
        reasons.append("全販売終了")
    # 開催日も過ぎていれば追加
    ev_date = ev.get('date', '')
    try:
        d = date.fromisoformat(ev_date)
        if d < today:
            reasons.append(f"開催終了{d}")
    except ValueError:
        pass
    return reasons


def perf_is_future(ev: dict, today: date) -> bool:
    """公演日(ev.date)が today 以降（未来 or 当日）なら True。
    日付が壊れている/不明なら「未来扱い(=保留側)」にして安全側に倒す。
    """
    ev_date = ev.get('date', '')
    try:
        return date.fromisoformat(ev_date) >= today
    except ValueError:
        return True


def fmt_event_entry(ev: dict, reasons: list) -> str:
    artist = ev.get('artist', '?')
    title = ev.get('title') or ev.get('event') or ev.get('name') or '?'
    venue = ev.get('venue', '?')
    d = ev.get('date', '?')
    return f"  id={ev.get('id')}: {artist} / {title} @ {venue} ({d}) [{', '.join(reasons)}]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--today', default=None, help='YYYY-MM-DD (デフォルト: 今日)')
    parser.add_argument('--report-file', default=None, help='レポート出力先')
    args = parser.parse_args()

    today = date.fromisoformat(args.today) if args.today else DEFAULT_TODAY

    out = [f"=== 期限切れチェック (today={today}) ==="]

    # index.html
    idx_events = extract_events_array('index.html')
    idx_flagged = [(ev, is_expired_index(ev, today)) for ev in idx_events]
    idx_flagged = [(ev, r) for ev, r in idx_flagged if r]
    # 「削除候補」と「⚠️要再確認(保留)」に振り分ける。
    # 要再確認に回す条件（機械判定だけで削除しない）:
    #   (a) saleEndUnknown=true … 販売終了日が不明で date に開始日等の仮置きをしているもの
    #   (b) 公演日(ev.date)がまだ未来 … 記録済みの販売枠が過ぎただけで、新しい販売枠
    #       （一般発売・コンビニ/ファミマ先行・当日券・リセール）が後から開く可能性が高い。
    #       しかも販売枠は当日の日中に開くので、朝の機械スナップショットでは枠ゼロに見えることがある。
    #       → 必ずWebFetchで再導出してから判断（2026-06-23 680私立恵比寿中学ファミマ先行を
    #         削除候補にしかけた事故の恒久対策。memory: feedback_pre_delete_webfetch_verify）
    # 削除候補に残るのは「公演も終わっている(ev.date < today)・かつ全販売終了」だけ。
    idx_delete, idx_recheck = [], []
    for ev, r in idx_flagged:
        if ev.get('saleEndUnknown') or perf_is_future(ev, today):
            idx_recheck.append((ev, r))
        else:
            idx_delete.append((ev, r))
    out.append(f"\n[index.html] 全{len(idx_events)}件 → 期限切れ削除候補(公演終了済) {len(idx_delete)}件 / ⚠️要再確認(公演は未来・要WebFetch) {len(idx_recheck)}件")
    for ev, r in idx_delete:
        out.append(fmt_event_entry(ev, r))
        for t in ev.get('tickets', []) or []:
            out.append(f"     - {t.get('type','?')}: {t.get('date','?')} soldout={t.get('soldout', False)}")
    if idx_recheck:
        out.append("\n  ⚠️ 以下は「公演がまだ未来」or saleEndUnknown=true。機械判定だけで削除しないこと。")
        out.append("     売り場URLをWebFetchで実態確認 → 新販売枠(一般/コンビニ先行/当日券)が出ていれば該当ticketを追加して変換、")
        out.append("     予定枚数終了/中止が確定したものだけ削除（抽選結果待ち・一般未発表は残置）:")
        for ev, r in idx_recheck:
            out.append(fmt_event_entry(ev, r))
            lk = ev.get('links', {}) or {}
            url = lk.get('rakuten') or lk.get('pia') or lk.get('eplus') or lk.get('lawson') or '(URLなし)'
            out.append(f"     URL: {url}")
            for t in ev.get('tickets', []) or []:
                out.append(f"     - {t.get('type','?')}: {t.get('date','?')}")

    # events.html（行楽）は2026-06-25に廃止。存在する時だけ後方互換でチェック。
    import os
    if os.path.exists('events.html'):
        ev_events = extract_events_array('events.html')
        ev_expired = [(ev, r) for ev, r in ((ev, is_expired_event(ev, today)) for ev in ev_events) if r]
        out.append(f"\n[events.html] 全{len(ev_events)}件 → 期限切れ {len(ev_expired)}件")
        for ev, r in ev_expired:
            out.append(fmt_event_entry(ev, r))

    text = '\n'.join(out)
    if args.report_file:
        with open(args.report_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"wrote {args.report_file}")
    else:
        # Windows cmd の文字化け対策: utf-8 で stdout に出す
        sys.stdout.reconfigure(encoding='utf-8')
        print(text)


if __name__ == '__main__':
    main()
