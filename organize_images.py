"""Downloadsフォルダの画像・動画から重複/類似ファイルを検出してまとめる."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import imagehash
from PIL import Image

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tif", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}

DEFAULT_THRESHOLD = 5  # 0-64, 小さいほど厳密
GROUP_DIR_NAME = "_organized"


def file_sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def image_phash(path: Path):
    try:
        with Image.open(path) as im:
            return imagehash.phash(im.convert("RGB"))
    except Exception as e:
        print(f"  [warn] 画像ハッシュ失敗 {path.name}: {e}", file=sys.stderr)
        return None


def video_phash(path: Path):
    cap = None
    try:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return None
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            return None
        cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
        ok, frame = cap.read()
        if not ok or frame is None:
            return None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return imagehash.phash(Image.fromarray(rgb))
    except Exception as e:
        print(f"  [warn] 動画ハッシュ失敗 {path.name}: {e}", file=sys.stderr)
        return None
    finally:
        if cap is not None:
            cap.release()


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def group_by_phash(items, threshold):
    n = len(items)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if items[i][1] - items[j][1] <= threshold:
                uf.union(i, j)
    groups = defaultdict(list)
    for i, (p, _) in enumerate(items):
        groups[uf.find(i)].append(p)
    return [g for g in groups.values() if len(g) >= 2]


def main() -> int:
    ap = argparse.ArgumentParser(description="Downloadsフォルダの画像・動画をまとめる")
    ap.add_argument("--execute", action="store_true", help="実際にファイルを移動する（既定はドライラン）")
    ap.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD, help="類似閾値 0-64 (小さいほど厳密)")
    ap.add_argument("--dir", type=Path, default=Path.home() / "Downloads", help="対象ディレクトリ")
    args = ap.parse_args()

    target: Path = args.dir
    if not target.is_dir():
        print(f"対象ディレクトリが見つかりません: {target}", file=sys.stderr)
        return 1

    print(f"対象      : {target}")
    print(f"モード    : {'本番実行' if args.execute else 'ドライラン'}")
    print(f"類似閾値  : {args.threshold}")
    print()

    images: list[Path] = []
    videos: list[Path] = []
    for p in target.iterdir():
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS:
            images.append(p)
        elif ext in VIDEO_EXTS:
            videos.append(p)
    print(f"画像 {len(images)}件 / 動画 {len(videos)}件")
    print()

    print("[1/3] 完全一致(SHA-256)を検出中...")
    exact_groups: dict[str, list[Path]] = defaultdict(list)
    for p in images + videos:
        try:
            exact_groups[file_sha256(p)].append(p)
        except Exception as e:
            print(f"  [warn] hash失敗 {p.name}: {e}", file=sys.stderr)
    exact_dups = [g for g in exact_groups.values() if len(g) >= 2]
    print(f"  完全一致グループ: {len(exact_dups)}件")
    exact_set: set[Path] = {p for g in exact_dups for p in g}

    print("[2/3] 画像の類似ハッシュ計算中...")
    img_hashes = []
    for p in images:
        if p in exact_set:
            continue
        h = image_phash(p)
        if h is not None:
            img_hashes.append((p, h))
    img_groups = group_by_phash(img_hashes, args.threshold)
    print(f"  画像類似グループ: {len(img_groups)}件")

    print("[3/3] 動画の類似ハッシュ計算中...")
    vid_hashes = []
    for p in videos:
        if p in exact_set:
            continue
        h = video_phash(p)
        if h is not None:
            vid_hashes.append((p, h))
    vid_groups = group_by_phash(vid_hashes, args.threshold)
    print(f"  動画類似グループ: {len(vid_groups)}件")
    print()

    base = target / GROUP_DIR_NAME
    group_idx = 0

    def handle(group: list[Path], kind: str):
        nonlocal group_idx
        group_idx += 1
        sub = base / f"{kind}_{group_idx:03d}"
        print(f"[{kind} #{group_idx}] -> {sub.name}/  ({len(group)}件)")
        for p in group:
            print(f"    {p.name}")
            if args.execute:
                sub.mkdir(parents=True, exist_ok=True)
                dest = sub / p.name
                i = 1
                while dest.exists():
                    dest = sub / f"{p.stem}_{i}{p.suffix}"
                    i += 1
                shutil.move(str(p), str(dest))

    print("===== 完全一致 =====")
    for g in exact_dups:
        kind = "exact_img" if g[0].suffix.lower() in IMAGE_EXTS else "exact_vid"
        handle(g, kind)

    print("===== 画像 類似 =====")
    for g in img_groups:
        handle(g, "sim_img")

    print("===== 動画 類似 =====")
    for g in vid_groups:
        handle(g, "sim_vid")

    print()
    if not args.execute:
        print("(ドライラン: 実際の移動はしていません。確定するには --execute を付けて実行してください)")
    else:
        print("完了しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
