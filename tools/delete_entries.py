#!/usr/bin/env python3
"""指定idのエントリをHTML内のEVENTS配列から削除する（毎朝の期限切れ削除用・恒久ツール）

使い方：
  python tools/delete_entries.py --file events.html --ids 1,17,82,179
  python tools/delete_entries.py --file index.html --ids 30,53

【方針】
- HTML内の `const EVENTS = [...];` 配列を JSON として読み、指定idを外して**読んだ時と同じ形**で書き戻す
  （🆕2026-09-24 行ベースの解析をやめた＝compact_events の「1件1行」でも動くように）
- 削除前にバックアップを取るのは呼び出し側の責任
"""
import argparse
import re
import sys


def find_entry_blocks(lines, start_idx, end_idx):
    """[start_idx, end_idx) 範囲のトップレベルエントリ {...} を検出。
    Returns: list of (entry_id, start_line_idx, end_line_idx)
    """
    blocks = []
    i = start_idx
    while i < end_idx:
        if lines[i].strip() == '{':
            entry_start = i
            depth = 1
            entry_id = None
            j = i + 1
            entry_end = None
            while j < end_idx and depth > 0:
                if entry_id is None:
                    m = re.search(r'"id":\s*(\d+)', lines[j])
                    if m:
                        entry_id = int(m.group(1))
                for ch in lines[j]:
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            entry_end = j
                            break
                if depth == 0:
                    break
                j += 1
            if entry_end is None:
                break
            blocks.append((entry_id, entry_start, entry_end))
            i = entry_end + 1
        else:
            i += 1
    return blocks


def delete_entries(filepath: str, del_ids: set):
    """🆕2026-09-24 行で数えるのをやめて JSON で読む＝indent=2 でも「1件1行」（compact_events）でも同じに動く。
    書き戻しは**読んだ時と同じ形**で（詰めてあれば詰めたまま・CRLFはCRLFのまま）。"""
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import compact_events as CE
    text = open(filepath, encoding='utf-8', newline='').read()
    s, end, events = CE.locate(text)
    compact = CE.is_compact(text)
    nl = '\r\n' if '\r\n' in text[:s] else '\n'
    print(f"{filepath}: {len(events)}件のエントリ検出（{'1件1行' if compact else 'indent=2'}）")
    found_ids = {e.get('id') for e in events if e.get('id') in del_ids}
    missing = del_ids - found_ids
    if missing:
        print(f"{filepath}: ⚠️ MISSING IDs (HTMLに見つからない): {sorted(missing)}")
    print(f"{filepath}: 削除実行 {len(found_ids)}件 → {sorted(found_ids)}")
    kept = [e for e in events if e.get('id') not in del_ids]
    new_text = text[:s] + CE.dump(kept, compact, nl) + text[end:]
    if CE.load(new_text) != kept:
        raise RuntimeError('書き戻した EVENTS が読み戻せない')
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(new_text)
    print(f"{filepath}: 書き込み完了")
    return len(found_ids)


def main():
    # Windows cmd の文字化け対策
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='対象HTMLファイル (index.html / events.html)')
    parser.add_argument('--ids', required=True, help='削除対象id（カンマ区切り）')
    args = parser.parse_args()

    ids = {int(x.strip()) for x in args.ids.split(',') if x.strip()}
    n = delete_entries(args.file, ids)
    print(f"\n[OK] {n}件削除完了")


if __name__ == '__main__':
    main()
