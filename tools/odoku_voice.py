# -*- coding: utf-8 -*-
"""お毒姐さんの声を作る（VOICEVOX＝無料・ローカル・商用可）。

なぜVOICEVOXか＝Veo/MiniMaxのAPIは無料枠が無く、あたし(Claude)が自動で回せるのは
ローカルで完結する合成だけ（2026-08-04調査）。声を自前で持てば「Hailuoが見た目から
声を決めて女性声になる」問題も根本から消える。

🎤 声の指定（2026-08-05 ユーザー確定・これが現行）＝
   **玄野武宏「ツンギレ」／抑揚1.0／音高-0.15／速度0.90**。
   ⚠️8/4は「抑揚2.0(最大)」だったが、実際の動画で聴いて**8/5に「抑揚をおさえて」で1.0に決定**。
   2.0は言葉が潰れて聞き取りづらかった。1.0/1.3/1.6を並べて聴き比べた結果。

🗣️ 台詞は**漢字混じりで書く**（2026-08-04 ユーザー方針転換）。ひらがなの羅列だと
   意味が伝わらないから。代わりに **--check で読みをカナで出して、間違った語だけ直す**。
   VOICEVOXが audio_query で「どう読むか」を返してくれるので機械で確認できる。

使い方:
  python tools/odoku_voice.py --serve-check                    # エンジンが動いてるか見る
  python tools/odoku_voice.py --script-file X.txt --check      # 読みだけ確認(音は作らない)
  python tools/odoku_voice.py --script-file X.txt --out tmp/voice/0805.wav

🚨 tmp/ には inspect.py があって標準ライブラリを隠すので、このツールは tools/ に置くこと。
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "http://127.0.0.1:50021"
# 🎤 2026-08-05 ユーザー確定＝玄野武宏「ツンギレ」・抑揚1.0・音高-0.15・速度0.90
#（白上虎太郎「びくびく」／玄野武宏「悲しみ」も試したが違うとのこと。
#  抑揚は8/4に2.0(最大)としたが、実物を聴いて8/5に1.0へ引き下げ＝2.0だと言葉が潰れる）
SPEAKER_NAME = "玄野武宏"
STYLE_NAME = "ツンギレ"
INTONATION = 1.0   # 抑揚（8/4は2.0だった・8/5にユーザー「抑揚をおさえて」で1.0）
PITCH = -0.15      # 音高
SPEED = 0.90       # 速度（1.0だと速くて聞き取りづらい・8/5確定）


def _get(path):
    with urllib.request.urlopen(HOST + path, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else b""
    req = urllib.request.Request(
        HOST + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def find_speaker(name=SPEAKER_NAME, style=STYLE_NAME):
    """話者IDを名前から機械で引く（IDを決め打ちしない）。"""
    names = []
    for sp in _get("/speakers"):
        names.append(sp["name"])
        if sp["name"] == name:
            for st in sp["styles"]:
                if st["name"] == style:
                    return st["id"]
            raise SystemExit(
                "%s のスタイル一覧に「%s」が無いわ → %s"
                % (name, style, [s["name"] for s in sp["styles"]])
            )
    raise SystemExit("話者「%s」が見つからないわ。いるのは→ %s" % (name, names))


def list_speakers():
    for sp in _get("/speakers"):
        print(sp["name"], "→", " / ".join("%s(%d)" % (s["name"], s["id"]) for s in sp["styles"]))


def build_query(script, speaker):
    q = urllib.parse.urlencode({"text": script, "speaker": speaker})
    return json.loads(_post("/audio_query?" + q).decode("utf-8"))


def kana_of(query):
    """audio_query が返す読み（カタカナ）。ここを見て読み間違いを探す。"""
    return query.get("kana", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="")
    ap.add_argument("--script-file", default="")
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "voice", "odoku.wav"))
    ap.add_argument("--intonation", type=float, default=INTONATION)
    ap.add_argument("--speed", type=float, default=SPEED)
    ap.add_argument("--pitch", type=float, default=PITCH)
    ap.add_argument("--speaker-name", default=SPEAKER_NAME)
    ap.add_argument("--style", default=STYLE_NAME)
    ap.add_argument("--check", action="store_true", help="読みだけ出して音は作らない")
    ap.add_argument("--serve-check", action="store_true")
    ap.add_argument("--list", action="store_true", help="話者とスタイルを全部出す")
    args = ap.parse_args()

    if args.list:
        list_speakers()
        return

    if args.serve_check:
        print("engine version:", _get("/version"))
        print("speaker id:", find_speaker(args.speaker_name, args.style),
              "=", args.speaker_name, args.style)
        return

    script = args.script
    if args.script_file:
        with open(args.script_file, encoding="utf-8") as f:
            script = f.read().strip()
    if not script:
        print("台詞が空よ（--script か --script-file を指定して）")
        sys.exit(1)

    speaker = find_speaker(args.speaker_name, args.style)
    query = build_query(script, speaker)

    print("台詞 %d字" % len(script))
    print("原文 :", script)
    print("読み :", kana_of(query))
    if args.check:
        print("※ 読みが違う語だけ、原文をひらがな/カタカナに直してもう一度")
        return

    query["intonationScale"] = args.intonation
    query["speedScale"] = args.speed
    query["pitchScale"] = args.pitch

    wav = _post("/synthesis?speaker=%d" % speaker, query)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(wav)
    print("%s  %d bytes  話者%d 抑揚%.2f 速度%.2f 音高%.2f"
          % (args.out, len(wav), speaker, query["intonationScale"],
             query["speedScale"], query["pitchScale"]))


main()
