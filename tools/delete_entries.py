#!/usr/bin/env python3
"""指定idのエントリをHTML内のEVENTS配列から削除する（毎朝の期限切れ削除用・恒久ツール）

使い方：
  python tools/delete_entries.py --file events.html --ids 1,17,82,179
  python tools/delete_entries.py --file index.html --ids 30,53

【方針】
- HTML内の `const EVENTS = [...];` 配列を行ベースに解析
- 指定idのエントリブロック ({...}) を行ごと削除
- 配列末尾の余計なカンマも調整
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
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    # EVENTS配列の範囲を見つける
    start_idx = None
    for idx, ln in enumerate(lines):
        if re.search(r'const\s+EVENTS\s*=\s*\[', ln):
            start_idx = idx
            break
    if start_idx is None:
        raise RuntimeError(f"{filepath}: const EVENTS not found")
    depth = 0
    in_array = False
    end_idx = None
    for idx in range(start_idx, len(lines)):
        for ch in lines[idx]:
            if ch == '[':
                depth += 1
                in_array = True
            elif ch == ']':
                depth -= 1
                if in_array and depth == 0:
                    end_idx = idx
                    break
        if end_idx is not None:
            break
    if end_idx is None:
        raise RuntimeError(f"{filepath}: array end not found")

    print(f"{filepath}: array lines {start_idx+1}-{end_idx+1}")
    blocks = find_entry_blocks(lines, start_idx + 1, end_idx)
    print(f"{filepath}: {len(blocks)}件のエントリ検出")

    to_delete = [b for b in blocks if b[0] in del_ids]
    found_ids = {b[0] for b in to_delete}
    missing = del_ids - found_ids
    if missing:
        print(f"{filepath}: ⚠️ MISSING IDs (HTMLに見つからない): {sorted(missing)}")
    print(f"{filepath}: 削除実行 {len(to_delete)}件 → {sorted(found_ids)}")

    del_line_set = set()
    for _, s, e in to_delete:
        for k in range(s, e + 1):
            del_line_set.add(k)

    new_lines = [ln for k, ln in enumerate(lines) if k not in del_line_set]
    new_text = ''.join(new_lines)
    # 配列末尾の余計なカンマ調整: "},\n  ];" → "}\n  ];"
    new_text = re.sub(r'},(\s*\n\s*\];)', r'}\1', new_text)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f"{filepath}: 書き込み完了")
    return len(to_delete)


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
