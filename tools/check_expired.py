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
    idx_expired = [(ev, is_expired_index(ev, today)) for ev in idx_events]
    idx_expired = [(ev, r) for ev, r in idx_expired if r]
    out.append(f"\n[index.html] 全{len(idx_events)}件 → 期限切れ {len(idx_expired)}件")
    for ev, r in idx_expired:
        out.append(fmt_event_entry(ev, r))
        for t in ev.get('tickets', []) or []:
            out.append(f"     - {t.get('type','?')}: {t.get('date','?')} soldout={t.get('soldout', False)}")

    # events.html
    ev_events = extract_events_array('events.html')
    ev_expired = [(ev, is_expired_event(ev, today)) for ev in ev_events]
    ev_expired = [(ev, r) for ev, r in ev_expired if r]
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
