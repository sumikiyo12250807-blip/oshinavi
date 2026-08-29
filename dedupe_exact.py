"""_organized/exact_* グループから1つだけ残して残りをゴミ箱へ送る."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from send2trash import send2trash

ORGANIZED_DIR = Path.home() / "Downloads" / "_organized"
DOWNLOADS = Path.home() / "Downloads"
SUFFIX_RE = re.compile(r"\s\(\d+\)$")  # 例: "foo (1)" にマッチ


def keeper_score(p: Path) -> tuple[int, int, str]:
    """残す優先順位 (小さいほど優先)."""
    has_suffix = 1 if SUFFIX_RE.search(p.stem) else 0
    return (has_suffix, len(p.name), p.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="実際にゴミ箱送り＆移動を行う")
    args = ap.parse_args()

    if not ORGANIZED_DIR.is_dir():
        print(f"見つかりません: {ORGANIZED_DIR}", file=sys.stderr)
        return 1

    groups = sorted(d for d in ORGANIZED_DIR.iterdir() if d.is_dir() and d.name.startswith("exact_"))
    print(f"対象グループ: {len(groups)}")
    print(f"モード: {'本番' if args.execute else 'ドライラン'}")
    print()

    total_kept = 0
    total_trashed = 0

    for g in groups:
        files = sorted([p for p in g.iterdir() if p.is_file()])
        if len(files) < 2:
            print(f"[skip] {g.name} ({len(files)}件)")
            continue
        files.sort(key=keeper_score)
        keep = files[0]
        trash = files[1:]

        # keep の戻し先 (衝突なら _NN を付ける)
        dest = DOWNLOADS / keep.name
        i = 1
        while dest.exists():
            dest = DOWNLOADS / f"{keep.stem}_{i}{keep.suffix}"
            i += 1

        print(f"[{g.name}]")
        print(f"  残す → {dest.name}")
        for t in trash:
            print(f"  ゴミ箱 → {t.name}")

        if args.execute:
            shutil.move(str(keep), str(dest))
            for t in trash:
                send2trash(str(t))
            try:
                g.rmdir()  # 空になったので削除
            except OSError:
                pass

        total_kept += 1
        total_trashed += len(trash)

    print()
    print(f"残す: {total_kept}件 / ゴミ箱送り: {total_trashed}件")
    if not args.execute:
        print("(ドライラン: --execute で本番実行)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
