# -*- coding: utf-8 -*-
"""MiniMax Music 3 を ComfyUI から使うためのノード（2026-08-29 作成）。

■ このPCでの前提（実測）
  ・GPU は Intel HD Graphics 620＝CUDA なし。MiniMax-Music3 のローカル実行は CUDA 必須で、
    ComfyUI 用の重みも最小構成（INT8）で約12GB。メモリ16GBのこのPCでは回らない。
  ・MiniMax 公式の音楽API は **2026-08-20 に新規ユーザーへ閉じられた**。
    実測で music-3.0 / music-2.6 / *-free すべて HTTP 410（status_code 2153）。
    → 公式APIは「既に音楽APIの課金実績があるアカウント」だけ使える。
  ・そこで **fal.ai 経由**（MiniMax Music 3 を1生成 $0.035 で提供）を既定にしてある。

■ プロバイダ
  provider = "fal"     … https://queue.fal.run/minimax/music-3（キュー方式・投げて待つ）
  provider = "minimax" … https://api.minimax.io/v1/music_generation（同期・既存課金者のみ）

■ 鍵の探し方（上から順に、見つかった1つを使う）
  fal      : 環境変数 FAL_KEY → このフォルダの fal_key.txt → ~/.fal_key
  minimax  : 環境変数 MINIMAX_API_KEY → このフォルダの api_key.txt
             → C:/Users/user/oshinavi/.minimax_key → ~/.minimax_key
"""
import io
import json
import os
import time
import urllib.request
import urllib.error

MINIMAX_URL = "https://api.minimax.io/v1/music_generation"
FAL_SUBMIT_URL = "https://queue.fal.run/minimax/music-3"

HERE = os.path.dirname(os.path.abspath(__file__))

KEY_FILES = {
    "minimax": [
        os.path.join(HERE, "api_key.txt"),
        r"C:/Users/user/oshinavi/.minimax_key",
        os.path.join(os.path.expanduser("~"), ".minimax_key"),
    ],
    "fal": [
        os.path.join(HERE, "fal_key.txt"),
        os.path.join(os.path.expanduser("~"), ".fal_key"),
    ],
}
KEY_ENV = {"minimax": "MINIMAX_API_KEY", "fal": "FAL_KEY"}


def _load_key(provider, explicit=""):
    """鍵を1本返す。無ければ「どこに置けばいいか」を書いて落とす（黙って進まない）。"""
    if explicit and explicit.strip():
        return explicit.strip()
    env = os.environ.get(KEY_ENV[provider], "").strip()
    if env:
        return env
    for p in KEY_FILES[provider]:
        if os.path.exists(p):
            # 🚨BOM付きで保存されていると鍵が壊れるので utf-8-sig で読む
            k = io.open(p, encoding="utf-8-sig").read().strip()
            if k:
                return k
    raise RuntimeError(
        "%s のAPIキーが見つからないわ。次のどれかを用意して:\n"
        "  ・環境変数 %s\n  ・%s"
        % (provider, KEY_ENV[provider], "\n  ・".join(KEY_FILES[provider]))
    )


def _http(url, key_header, payload=None, method="GET", timeout=120):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = dict(key_header)
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:900]
        raise RuntimeError("%s が HTTP %d を返したわ:\n%s" % (url, e.code, body))


def _to_audio(audio_bytes):
    """mp3/wav のバイト列 → ComfyUI の AUDIO 型（waveform, sample_rate）"""
    import torchaudio
    wav, sr = torchaudio.load(io.BytesIO(audio_bytes))
    if wav.dim() == 2:
        wav = wav.unsqueeze(0)              # (batch, channels, samples)
    return {"waveform": wav, "sample_rate": sr}


def _validate(prompt, lyrics, is_instrumental, lyrics_optimizer):
    prompt = (prompt or "").strip()
    lyrics = (lyrics or "").strip()
    if not prompt:
        raise RuntimeError("prompt（曲の説明）は必須よ。1〜2000字で入れて。")
    if len(prompt) > 2000:
        raise RuntimeError("prompt が %d 字。上限は2000字よ。" % len(prompt))
    if len(lyrics) > 3500:
        raise RuntimeError("lyrics が %d 字。上限は3500字よ。" % len(lyrics))
    if not is_instrumental and not lyrics_optimizer and not lyrics:
        raise RuntimeError(
            "歌ありの時は lyrics が要るわ（1〜3500字）。"
            "歌詞を自動生成させるなら lyrics_optimizer を ON、"
            "歌なしなら is_instrumental を ON にして。")
    return prompt, lyrics


# ----------------------------------------------------------------- fal.ai
def _run_fal(key, prompt, lyrics, is_instrumental, duration, steps,
             guidance, seed, timeout_sec):
    hdr = {"Authorization": "Key " + key}
    # fal は歌なし指定が無いので、歌詞欄に器楽指定を入れる（公式の作法）
    if is_instrumental or not lyrics:
        lyrics = "[instrumental]"
    payload = {"prompt": prompt, "lyrics": lyrics,
               "duration": float(duration),
               "num_inference_steps": int(steps),
               "guidance_scale": float(guidance)}
    if seed and int(seed) > 0:
        payload["seed"] = int(seed)

    sub = _http(FAL_SUBMIT_URL, hdr, payload, method="POST", timeout=60)
    status_url = sub.get("status_url")
    response_url = sub.get("response_url")
    req_id = sub.get("request_id")
    if not status_url or not response_url:
        raise RuntimeError("fal の応答に status_url が無いわ: %s"
                           % json.dumps(sub, ensure_ascii=False)[:400])

    t0 = time.time()
    while True:
        st = _http(status_url, hdr, timeout=60)
        s = st.get("status")
        if s == "COMPLETED":
            break
        if s in ("FAILED", "CANCELLED", "ERROR"):
            raise RuntimeError("fal の生成が %s になったわ: %s"
                               % (s, json.dumps(st, ensure_ascii=False)[:500]))
        if time.time() - t0 > timeout_sec:
            raise RuntimeError("fal が %d 秒で終わらなかったわ（request_id=%s）。"
                               "timeout_sec を伸ばして。" % (timeout_sec, req_id))
        time.sleep(3.0)

    res = _http(response_url, hdr, timeout=120)
    url = ((res.get("audio") or {}).get("url"))
    if not url:
        raise RuntimeError("fal の結果に音声URLが無いわ: %s"
                           % json.dumps(res, ensure_ascii=False)[:500])
    audio_bytes = urllib.request.urlopen(url, timeout=180).read()
    info = "fal / minimax/music-3 / %.1f秒 / seed=%s / 所要 %.1f秒 / request_id=%s" % (
        float(res.get("duration") or 0), res.get("seed"), time.time() - t0, req_id)
    return _to_audio(audio_bytes), info


# ------------------------------------------------------------ MiniMax公式
def _run_minimax(key, model, prompt, lyrics, is_instrumental, lyrics_optimizer,
                 fmt, sample_rate, bitrate, timeout_sec):
    payload = {
        "model": model,
        "prompt": prompt,
        "is_instrumental": bool(is_instrumental),
        "lyrics_optimizer": bool(lyrics_optimizer),
        "stream": False,
        "output_format": "hex",
        "audio_setting": {"sample_rate": int(sample_rate),
                          "bitrate": int(bitrate), "format": fmt},
    }
    if lyrics:
        payload["lyrics"] = lyrics
    t0 = time.time()
    res = _http(MINIMAX_URL, {"Authorization": "Bearer " + key}, payload,
                method="POST", timeout=timeout_sec)
    base = res.get("base_resp") or {}
    if base.get("status_code") not in (0, None):
        raise RuntimeError("MiniMax API エラー %s: %s"
                           % (base.get("status_code"), base.get("status_msg")))
    hexstr = (res.get("data") or {}).get("audio")
    if not hexstr:
        raise RuntimeError("音声が返ってこなかったわ: %s"
                           % json.dumps(res, ensure_ascii=False)[:500])
    ex = res.get("extra_info") or {}
    info = "minimax公式 / %s / %.1f秒 / 所要 %.1f秒 / trace=%s" % (
        model, (int(ex.get("music_duration") or 0) / 1000.0),
        time.time() - t0, res.get("trace_id"))
    return _to_audio(bytes.fromhex(hexstr)), info


class MiniMaxMusicAPIKey:
    """鍵を明示的に渡したい時だけ使う。空なら自動で探すわ。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "provider": (["fal", "minimax"], {"default": "fal"}),
            "api_key": ("STRING", {"default": "", "multiline": False}),
        }}

    RETURN_TYPES = ("MINIMAX_KEY",)
    RETURN_NAMES = ("key",)
    FUNCTION = "run"
    CATEGORY = "MiniMax Music"

    def run(self, provider, api_key):
        return ((provider, _load_key(provider, api_key)),)


class MiniMaxMusic3:
    """MiniMax Music 3 で曲を1本つくる（クラウド生成・GPU不要）。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "provider": (["fal", "minimax"], {"default": "fal"}),
                "prompt": ("STRING", {"multiline": True,
                                      "default": "J-pop, bright and uplifting, female vocal, piano and strings"}),
                "lyrics": ("STRING", {"multiline": True,
                                      "default": "[verse]\n朝の光が窓を叩く\n[chorus]\n走り出そう 今日という日へ"}),
                "is_instrumental": ("BOOLEAN", {"default": False}),
                "timeout_sec": ("INT", {"default": 900, "min": 60, "max": 3600}),
            },
            "optional": {
                "key": ("MINIMAX_KEY",),
                # fal 用
                "duration": ("FLOAT", {"default": 60.0, "min": 10.0, "max": 300.0, "step": 1.0}),
                "num_inference_steps": ("INT", {"default": 30, "min": 5, "max": 100}),
                "guidance_scale": ("FLOAT", {"default": 1.7, "min": 0.1, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**31 - 1}),
                # minimax公式 用
                "minimax_model": (["music-3.0", "music-3.0-free", "music-2.6", "music-2.6-free"],
                                  {"default": "music-3.0"}),
                "lyrics_optimizer": ("BOOLEAN", {"default": False}),
                "format": (["mp3", "wav"], {"default": "mp3"}),
                "sample_rate": ([44100, 32000, 24000, 16000], {"default": 44100}),
                "bitrate": ([256000, 128000, 64000, 32000], {"default": 256000}),
            },
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "info")
    FUNCTION = "run"
    CATEGORY = "MiniMax Music"

    def run(self, provider, prompt, lyrics, is_instrumental, timeout_sec,
            key=None, duration=60.0, num_inference_steps=30, guidance_scale=1.7,
            seed=0, minimax_model="music-3.0", lyrics_optimizer=False,
            format="mp3", sample_rate=44100, bitrate=256000):

        if key:
            provider, api_key = key
        else:
            api_key = _load_key(provider)

        prompt, lyrics = _validate(prompt, lyrics, is_instrumental, lyrics_optimizer)

        if provider == "fal":
            return _run_fal(api_key, prompt, lyrics, is_instrumental, duration,
                            num_inference_steps, guidance_scale, seed, timeout_sec)
        return _run_minimax(api_key, minimax_model, prompt, lyrics, is_instrumental,
                            lyrics_optimizer, format, sample_rate, bitrate, timeout_sec)


NODE_CLASS_MAPPINGS = {
    "MiniMaxMusic3": MiniMaxMusic3,
    "MiniMaxMusicAPIKey": MiniMaxMusicAPIKey,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "MiniMaxMusic3": "MiniMax Music 3 (Cloud)",
    "MiniMaxMusicAPIKey": "MiniMax Music API Key",
}
