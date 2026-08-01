# -*- coding: utf-8 -*-
"""お毒姐さんにX投稿を読ませる動画を MiniMax H3 で作る。

使い方:
  set MINIMAX_API_KEY=...            (PowerShell なら $env:MINIMAX_API_KEY="...")
  python tools/x_video.py --script "はぁ？8月2日発売よ。まだ知らないの？" --dry-run
  python tools/x_video.py --script-file tmp/x_video_script.txt --out tmp/video/0802.mp4

仕様メモ(公式ドキュメント実測 2026-08-01):
  作成   POST https://api.minimax.io/v2/video_generation
  照会   GET  https://api.minimax.io/v2/query/video_generation/{task_id}
  duration は 4〜15秒・resolution は "2K" のみ・参照画像は reference_image ロールで最大9枚。
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

API_CREATE = "https://api.minimax.io/v2/video_generation"
API_QUERY = "https://api.minimax.io/v2/query/video_generation/{task_id}"
MODEL = "MiniMax-H3"

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REFS = [
    os.path.join(REPO, "tmp", "char", "odoku_front.png"),
    os.path.join(REPO, "tmp", "char", "odoku_smile.png"),
]

# 日本語の朗読はだいたい秒5字。尺に収まらないセリフを投げると途中で切れる。
CHARS_PER_SEC = 5.0

# キャラの見た目を毎回同じ言葉で固定する（参照画像だけに頼らない）。
CHARACTER = (
    "A stylized 3D-cartoon Japanese woman in her forties, plus-size, "
    "lavender bouffant updo with a small tiara, dramatic purple eyeshadow, "
    "a beauty mark on her right cheek, large jeweled earrings, "
    "a sparkling lavender sequined dress with a matching sequined cape, "
    "pastel lavender studio background, warm key light, Pixar-like rendering."
)

SCENE = (
    "Medium shot, camera locked off, she faces the viewer and speaks directly to camera "
    "with lively theatrical gestures, confident and teasing, ending with a warm smile. "
    "Accurate Japanese lip sync. Clear female voice, slightly husky, playful. "
    "No on-screen text, no subtitles, no watermark."
)


def build_prompt(script: str, extra: str = "") -> str:
    parts = [CHARACTER, SCENE, "She says in Japanese: 「" + script + "」"]
    if extra:
        parts.append(extra)
    return " ".join(parts)


def as_image_url(path_or_url: str) -> str:
    """http(s) はそのまま。ローカルファイルは data URI にする。
    ※ data URI を受け付けるかは未検証。弾かれたら oshinavi.jp に画像を置いて公開URLを渡すこと。
    """
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    if not os.path.exists(path_or_url):
        sys.exit("参照画像が見つからない: " + path_or_url)
    mime = mimetypes.guess_type(path_or_url)[0] or "image/png"
    with open(path_or_url, "rb") as f:
        return "data:" + mime + ";base64," + base64.b64encode(f.read()).decode("ascii")


def post_json(url: str, payload: dict, key: str) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def get_json(url: str, key: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", "Bearer " + key)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="お毒姐さんに言わせる日本語のセリフ")
    ap.add_argument("--script-file", help="セリフをファイルから読む")
    ap.add_argument("--duration", type=int, default=15, help="4〜15秒 (既定15)")
    ap.add_argument("--ratio", default="16:9", help="16:9 / 9:16 / 1:1 など")
    ap.add_argument("--ref", action="append", help="参照画像(パス or URL)。省略時は tmp/char の2枚")
    ap.add_argument("--extra", default="", help="プロンプトに足したい指示")
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "video", "odoku.mp4"))
    ap.add_argument("--dry-run", action="store_true", help="投げずにpayloadだけ表示（課金されない）")
    ap.add_argument("--poll", type=int, default=10, help="照会の間隔(秒)")
    ap.add_argument("--timeout", type=int, default=900, help="完了待ちの上限(秒)")
    args = ap.parse_args()

    if args.script_file:
        with open(args.script_file, encoding="utf-8") as f:
            script = f.read().strip()
    elif args.script:
        script = args.script.strip()
    else:
        sys.exit("--script か --script-file が要る")

    if not 4 <= args.duration <= 15:
        sys.exit("duration は 4〜15 の範囲")

    limit = int(args.duration * CHARS_PER_SEC)
    print("セリフ %d字 / 尺%d秒に収まる目安 %d字" % (len(script), args.duration, limit))
    if len(script) > limit:
        print("⚠️ 長すぎ＝読み切れずに切れる。%d字まで削ること。" % limit)

    refs = args.ref if args.ref else [p for p in DEFAULT_REFS if os.path.exists(p)]
    if not refs:
        print("⚠️ 参照画像なしで生成する＝キャラの同一性は担保されない")

    content = [{"type": "text", "text": build_prompt(script, args.extra)}]
    for r in refs:
        content.append({"type": "image_url", "image_url": {"url": as_image_url(r)}, "role": "reference_image"})

    payload = {
        "model": MODEL,
        "content": content,
        "duration": args.duration,
        "resolution": "2K",
        "ratio": args.ratio,
    }

    if args.dry_run:
        preview = json.loads(json.dumps(payload))
        for c in preview["content"]:
            if c.get("type") == "image_url":
                u = c["image_url"]["url"]
                c["image_url"]["url"] = u[:60] + "...(%d文字)" % len(u) if len(u) > 60 else u
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        print("参照画像 %d枚 / --dry-run なので送信していない" % len(refs))
        return

    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if not key:
        sys.exit("環境変数 MINIMAX_API_KEY が空。platform.minimax.io で発行して設定して。")

    try:
        res = post_json(API_CREATE, payload, key)
    except urllib.error.HTTPError as e:
        sys.exit("作成失敗 HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:500]))
    task_id = res.get("task_id") or (res.get("task") or {}).get("id")
    if not task_id:
        sys.exit("task_id が返らない: " + json.dumps(res, ensure_ascii=False)[:500])
    print("task_id:", task_id)

    started = time.time()
    video_url = None
    while time.time() - started < args.timeout:
        time.sleep(args.poll)
        try:
            q = get_json(API_QUERY.format(task_id=task_id), key)
        except urllib.error.HTTPError as e:
            print("照会エラー HTTP %s（続行）" % e.code)
            continue
        task = q.get("task") or q
        status = task.get("status")
        print("  %4ds status=%s" % (int(time.time() - started), status))
        if status in ("succeeded", "success", "Success"):
            video_url = (task.get("content") or {}).get("url") or task.get("file_url")
            break
        if status in ("failed", "Fail"):
            sys.exit("生成失敗: " + json.dumps(q, ensure_ascii=False)[:500])
    if not video_url:
        sys.exit("時間切れ。task_id %s を後で照会して。" % task_id)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with urllib.request.urlopen(video_url, timeout=300) as r, open(args.out, "wb") as f:
        f.write(r.read())
    print("保存:", args.out, os.path.getsize(args.out), "bytes")


if __name__ == "__main__":
    main()
