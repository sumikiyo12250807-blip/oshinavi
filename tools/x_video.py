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
# 参照画像は1枚だけ渡す（image-to-videoは1コマ目として使われる）。
# 2026-08-04のキャラ刷新後は tmp/char3 のもの。大きい正面画ができたら差し替える。
DEFAULT_REFS = [
    os.path.join(REPO, "tmp", "char3", "ref_front.png"),
]

# 日本語の朗読はだいたい秒5字。尺に収まらないセリフを投げると途中で切れる。
CHARS_PER_SEC = 5.0

# 🚨【声の指定は必ず最先頭】(2026-08-02 実機で判明)
# Hailuoは「見た目」から声を決めるので、女性に見える絵だと女声になる。声の形容詞を後ろに
# 足しても効かなかった。対策は①声の指定を最初に置く ②身元を「ドラァグをする男性」と書く
# ③代名詞を he/his に統一 の3点セット。お毒姐さんはおねえ＝**男性の声**が正
# （ユーザー「澄んだ女性の声はだめ」）。それでも駄目ならリップシンク型へ切替。
VOICE = (
    "VOICE REQUIREMENT (highest priority): the speaking voice MUST be a MAN's voice — "
    "a warm, low-pitched adult male voice speaking Japanese, campy and theatrical, "
    "the voice of a Japanese drag queen. NEVER a female voice, never a clear high voice."
)

# キャラの見た目を毎回同じ言葉で固定する（参照画像だけに頼らない）。
# 🚨 2026-08-05修正＝ここが【旧キャラのまま】だった。8/4にコメントだけ「キャラ刷新」と
#    書き換えて本文を直し忘れていた＝参照画像(新キャラ)と文章(旧キャラ)が矛盾する状態。
#    dry-run で気づいて課金前に修正（気づかなければ$1.30で別人が出るところだった）。
# 🎨 現行キャラ＝tmp/char6（2026-08-06 ユーザー指定「今日はこのキャラでやってみる」）。
#    紫スパンコールのぽっちゃりドラァグクイーン。前キャラ(char3の黒髪ショート)から差し替えた。
CHARACTER = (
    "The speaker is a stylized 3D-rendered cartoon Japanese drag queen: a short, very "
    "plump MAN performing in drag, with a tall lavender-purple bouffant updo topped by "
    "a small jewelled tiara, round full cheeks, heavy purple eyeshadow with long lashes "
    "and sharp winged eyeliner, pink glossy lips, a beauty mark on the cheek, large "
    "purple gemstone drop earrings and matching necklace, wearing a shimmering "
    "lilac-and-silver sequinned dress with a matching sequinned long duster coat draped "
    "over it, warm, campy, bossy and theatrical."
)

# 🚨 2026-08-05修正＝"Medium shot"(バストアップ)固定をやめた。参照画像の構図は毎回変わる
#    （この日は「全身を小さめに右下」）ので、寄りを言葉で決め打ちすると絵と喧嘩する。
# 🚨🚨 2026-08-06修正＝**"subtle theatrical gestures"(控えめな仕草)が動きを殺していた**。
#    ユーザー「もうちょっと動きが欲しいよね」。背景の文字を守りたい一心で
#    「カメラ固定・背景固定・動くのは本人だけ」と書いたうえに、本人の芝居まで
#    "subtle" と指定していた＝守る必要があるのは**カメラと背景**であって、本人の動きではない。
#    → カメラ/背景のロックは残したまま、本人には**大きく連続した仕草**を要求する。
#    その場から動かない1行を足して、画面外へ出たり背景を踏み荒らすのを防ぐ。
SCENE = (
    "Camera locked off. Keep exactly the same framing, scale and position as the "
    "reference image — do not zoom, pan or re-compose. "
    "He performs to camera with BIG, continuous, exaggerated drag-queen gestures: "
    "he lifts and wags his index finger, opens both arms wide, puts a hand on his hip "
    "and tilts his head, shrugs, points at the viewer, and finishes with a wink and a "
    "warm smile. Constant lively motion of head, shoulders, hands and hair throughout "
    "the whole shot — never a still pose. He stays standing in the same spot and never "
    "leaves the frame. Accurate Japanese lip sync. "
    "No on-screen text, no subtitles, no watermark."
)

# 🎉 背景を守る指示（2026-08-04に実証＝これを付けたらX投稿の文字が1文字も崩れなかった）。
# 参照画像に投稿画面を合成して渡すので、背景を描き直されると文字が壊れる。既定で必ず付ける。
BACKGROUND = (
    "Keep the background perfectly still and pixel-identical to the reference image: "
    "do NOT redraw, re-render or alter any text, letters, numbers or the logo anywhere "
    "in the frame. Only the drag queen herself moves."
)


# 🎤【音声を渡す場合】声はこちらが用意した音声（VOICEVOX 玄野武宏ツンギレ）を使うので、
# 「男性の声にしろ」という指示は不要になる。代わりに「渡した音声に口を合わせろ」と言う。
# こうすれば**毎回まったく同じ声**になる＝Hailuoが見た目から声を決める問題が根本から消える。
VOICE_GIVEN = (
    "AUDIO REQUIREMENT (highest priority): the provided audio IS the character's own "
    "speaking voice. Lip-sync his mouth precisely and naturally to that Japanese audio, "
    "matching every syllable. Do not generate any other voice, narration or speech."
)


# 🎙️【声だけ借りる場合＝ボイストランスファー】(2026-08-06 ユーザー方針)
# 参照音声を「この台詞を喋らせる元データ」ではなく「声色(音色)の見本」として使う。
# 中身は喋らせず、**その声で新しい台詞**を喋らせる。H3の公式仕様に
# 「Reference character, motion, camera, style, voice」＝voiceの参照が挙がっている。
# 使い道＝H3が自力で出した"当たりの声"を1本目から抜き出して見本にすれば、
# VOICEVOXの合成音に頼らず**毎回同じ声**にできる（参照音声は無料）。
VOICE_CLONE = (
    "VOICE REQUIREMENT (highest priority): the provided reference audio is a sample of "
    "THIS character's voice timbre only. Reproduce that exact same voice — same timbre, "
    "same pitch, same age, same masculine drag-queen character — but he speaks the NEW "
    "Japanese line written below. Do NOT repeat or replay the words contained in the "
    "reference audio. Accurate Japanese lip sync to the new line."
)


def build_prompt(script: str, extra: str = "", audio_given: bool = False,
                 voice_ref: bool = False) -> str:
    if voice_ref:
        parts = [VOICE_CLONE, CHARACTER, SCENE, BACKGROUND,
                 "He says in Japanese: 「" + script + "」"]
    elif audio_given:
        parts = [VOICE_GIVEN, CHARACTER, SCENE, BACKGROUND,
                 "The audio says in Japanese: 「" + script + "」"]
    else:
        parts = [VOICE, CHARACTER, SCENE, BACKGROUND,
                 "He says in Japanese: 「" + script + "」"]
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


KEY_FILE = os.path.join(REPO, ".minimax_key")


def load_key() -> str:
    """APIキーは ①環境変数 MINIMAX_API_KEY ②リポジトリ直下の .minimax_key の順で探す。
    ファイル方式にしたのは、キーをチャットや git に出さずに渡すため（.gitignore 済み）。
    """
    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if key:
        return key
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, encoding="utf-8-sig") as f:
            key = f.read().strip().strip('"').strip("'")
        if key:
            return key
        sys.exit(".minimax_key は在るが中身が空。キーだけを1行で保存して。")
    sys.exit(
        "APIキーが見つからない。次のどちらかで渡して:\n"
        "  ① メモ帳にキーだけ貼って " + KEY_FILE + " という名前で保存\n"
        "  ② $env:MINIMAX_API_KEY=\"...\" を設定"
    )


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
    # 既定は縦(9:16)。Xのタイムラインは縦が大きく出るし、実機の初号2本も9:16で作った。
    ap.add_argument("--ratio", default="9:16", help="9:16(既定) / 16:9 / 1:1 など")
    ap.add_argument("--ref", action="append", help="参照画像(パス or URL)。省略時は DEFAULT_REFS")
    ap.add_argument("--audio", action="append",
                    help="読ませる音声(wav/mp3・2〜15秒・15MB以下)。渡すと声が毎回同じになる")
    ap.add_argument("--voice-ref", action="store_true",
                    help="--audio を『声色の見本』として使う（中身は喋らせず、その声で新しい台詞を喋らせる）")
    ap.add_argument("--extra", default="", help="プロンプトに足したい指示")
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "video", "odoku.mp4"))
    ap.add_argument("--dry-run", action="store_true", help="投げずにpayloadだけ表示（課金されない）")
    ap.add_argument("--poll", type=int, default=10, help="照会の間隔(秒)")
    ap.add_argument("--timeout", type=int, default=900, help="完了待ちの上限(秒)")
    args = ap.parse_args()

    if args.script_file:
        # VOICEVOXの書き出しtxtはBOM付きなので utf-8-sig で読む
        with open(args.script_file, encoding="utf-8-sig") as f:
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

    # 🚨台詞は「ひらがな＋カタカナ」で書く（AIは漢字の読みを外す＝平手友梨奈/14時 等）。
    # 固有名詞と数字がいちばん危ないので、漢字が残っていたら止めずに警告する。
    kanji = [c for c in script if "一" <= c <= "鿿"]
    if kanji:
        print("⚠️ 漢字が%d字ある＝読み間違いの元。ひらがなに開くこと: %s"
              % (len(kanji), "".join(sorted(set(kanji)))))
    if any("0" <= c <= "9" or "０" <= c <= "９" for c in script):
        print("⚠️ 数字は漢数字でなく『じゅうよじ』のように かな で書くと読みが安定する")

    refs = args.ref if args.ref else [p for p in DEFAULT_REFS if os.path.exists(p)]
    if not refs:
        print("⚠️ 参照画像なしで生成する＝キャラの同一性は担保されない")

    if args.voice_ref and not args.audio:
        sys.exit("--voice-ref は --audio(声の見本) と一緒に使う")

    content = [{"type": "text", "text": build_prompt(
        script, args.extra, bool(args.audio), args.voice_ref)}]
    for r in refs:
        content.append({"type": "image_url", "image_url": {"url": as_image_url(r)}, "role": "reference_image"})

    # 🎤 音声を渡す＝声を毎回同じにできる（公式仕様 2026-08-04 実測）:
    #   {"type":"audio_url","audio_url":{"url":...},"role":"reference_audio"}
    #   最大3クリップ／2〜15秒・合計15秒以下／WAV・MP3／15MB以下／画像か動画と併用が必須
    if args.audio:
        for a in args.audio:
            content.append({"type": "audio_url",
                            "audio_url": {"url": as_image_url(a)},
                            "role": "reference_audio"})

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
            for k in ("image_url", "audio_url"):
                if c.get("type") == k:
                    u = c[k]["url"]
                    c[k]["url"] = u[:60] + "...(%d文字)" % len(u) if len(u) > 60 else u
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        print("参照画像 %d枚 / 音声 %d本 / --dry-run なので送信していない"
              % (len(refs), len(args.audio or [])))
        return

    key = load_key()

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
