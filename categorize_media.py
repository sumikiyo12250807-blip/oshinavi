"""Downloadsの画像・動画を 写真/塗り絵/イラスト/動画 に分類して移動する."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

DOWNLOADS = Path.home() / "Downloads"

CAT_DIRS = {
    "photo": DOWNLOADS / "写真",
    "coloring": DOWNLOADS / "塗り絵",
    "illustration": DOWNLOADS / "イラスト",
    "video": DOWNLOADS / "動画",
}

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tif", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}

COLORING_KEYS = ["coloring", "mandala", "塗り絵", "塗りえ", "ぬりえ"]
ILLUST_KEYS = [
    "chatgpt image", "gemini_generated", "gemini-2.5", "nano-banana",
    "logo", "ロゴ", "banner", "バナー", "デザイン", "design",
    "icon", "アイコン", "wallpaper", "壁紙",
]

# Downloads直下で除外するフォルダ名 (再帰しない)
TOP_SKIP = {"写真", "塗り絵", "イラスト", "動画"}
# Downloads配下で再帰展開するフォルダ
EXPAND_DIRS = {"_organized"}


def classify_image(path: Path) -> str:
    name = path.name.lower()

    if any(k in name for k in COLORING_KEYS):
        return "coloring"
    if any(k in name for k in ILLUST_KEYS):
        return "illustration"

    return analyze_image(path)


def analyze_image(path: Path) -> str:
    try:
        with Image.open(path) as im:
            has_exif = bool(im.getexif())
            im_rgb = im.convert("RGB")
            im_rgb.thumbnail((128, 128))

        arr = np.asarray(im_rgb).astype(np.float32) / 255.0  # HxWx3
        gray = arr.mean(axis=2)
        very_light = (gray > 240 / 255).sum() / gray.size

        mx = arr.max(axis=2)
        mn = arr.min(axis=2)
        sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-9), 0.0)
        mean_sat = float(sat.mean())

        # 塗り絵: 彩度ほぼ無し & 白ベース
        if mean_sat < 0.08 and very_light > 0.55:
            return "coloring"

        # EXIFあり → 写真
        if has_exif:
            return "photo"

        # 色の多さ (32x32に縮小して unique RGB を数える)
        small = np.asarray(im_rgb.resize((32, 32))).reshape(-1, 3)
        unique_colors = np.unique(small, axis=0).shape[0]

        if unique_colors > 800 and mean_sat > 0.15:
            return "photo"

        return "illustration"
    except Exception as e:
        print(f"  [warn] 画像解析失敗 {path.name}: {e}", file=sys.stderr)
        return "illustration"


def collect_files() -> list[Path]:
    files: list[Path] = []
    for entry in DOWNLOADS.iterdir():
        if entry.is_file():
            ext = entry.suffix.lower()
            if ext in IMAGE_EXTS or ext in VIDEO_EXTS:
                files.append(entry)
        elif entry.is_dir():
            if entry.name in TOP_SKIP:
                continue
            if entry.name in EXPAND_DIRS:
                for p in entry.rglob("*"):
                    if p.is_file():
                        ext = p.suffix.lower()
                        if ext in IMAGE_EXTS or ext in VIDEO_EXTS:
                            files.append(p)
    return files


def unique_dest(directory: Path, name: str) -> Path:
    dest = directory / name
    if not dest.exists():
        return dest
    stem, suffix = Path(name).stem, Path(name).suffix
    i = 1
    while True:
        cand = directory / f"{stem}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="実際に移動する (既定はドライラン)")
    ap.add_argument("--show", type=int, default=10, help="各カテゴリのサンプル表示件数")
    args = ap.parse_args()

    if not DOWNLOADS.is_dir():
        print(f"Downloads が見つかりません: {DOWNLOADS}", file=sys.stderr)
        return 1

    files = collect_files()
    print(f"対象ファイル: {len(files)}件")
    print(f"モード: {'本番' if args.execute else 'ドライラン'}")
    print()

    plan: dict[str, list[tuple[Path, Path]]] = {k: [] for k in CAT_DIRS}

    for p in files:
        ext = p.suffix.lower()
        if ext in VIDEO_EXTS:
            cat = "video"
        else:
            cat = classify_image(p)
        dest_dir = CAT_DIRS[cat]
        dest = unique_dest(dest_dir, p.name) if args.execute else dest_dir / p.name
        plan[cat].append((p, dest))

    counts = {k: len(v) for k, v in plan.items()}
    print(f"分類結果: 写真 {counts['photo']} / 塗り絵 {counts['coloring']} / "
          f"イラスト {counts['illustration']} / 動画 {counts['video']}")
    print()

    label = {"photo": "写真", "coloring": "塗り絵", "illustration": "イラスト", "video": "動画"}
    for cat, items in plan.items():
        print(f"===== {label[cat]} ({len(items)}件) =====")
        for src, _ in items[: args.show]:
            print(f"  {src.relative_to(DOWNLOADS)}")
        if len(items) > args.show:
            print(f"  ... 他 {len(items) - args.show} 件")
        print()

    if not args.execute:
        print("(ドライラン: --execute で本番実行)")
        return 0

    # 本番実行
    for cat, items in plan.items():
        CAT_DIRS[cat].mkdir(parents=True, exist_ok=True)

    moved = 0
    errors = 0
    for cat, items in plan.items():
        for src, _ in items:
            dest = unique_dest(CAT_DIRS[cat], src.name)
            try:
                shutil.move(str(src), str(dest))
                moved += 1
            except Exception as e:
                print(f"  [error] 移動失敗 {src}: {e}", file=sys.stderr)
                errors += 1

    # _organized の空サブフォルダ・空 _organized を掃除
    organized = DOWNLOADS / "_organized"
    if organized.is_dir():
        for sub in sorted(organized.iterdir(), reverse=True):
            if sub.is_dir():
                try:
                    sub.rmdir()
                except OSError:
                    pass
        try:
            organized.rmdir()
        except OSError:
            pass

    print()
    print(f"移動完了: {moved}件 / エラー: {errors}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
