# -*- coding: utf-8 -*-
"""抑揚を変えた音声を何本か作る（ユーザー指示 2026-08-05「抑揚をおさえて」）。

VOICEVOXが落ちていたら起動して待つ（ポート50021）。
声の他の条件は据え置き＝玄野武宏「ツンギレ」／音高-0.15／速度0.90。
"""
import io
import os
import subprocess
import sys
import time
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
EXE = r"C:\Users\user\OneDrive\デスクトップ\VOICEVOX\VOICEVOX.exe"
HOST = "http://127.0.0.1:50021"
SCRIPT = os.path.join(ROOT, "tmp", "odoku_script_0805.txt")


def alive():
    try:
        urllib.request.urlopen(HOST + "/speakers", timeout=3).read(64)
        return True
    except Exception:
        return False


if not alive():
    print("VOICEVOXが止まっているので起動する…")
    subprocess.Popen([EXE], shell=False)
    for i in range(60):
        time.sleep(3)
        if alive():
            print("  起動した（%d秒）" % ((i + 1) * 3))
            break
    else:
        print("🚨 90秒待っても起動しなかった")
        sys.exit(1)
else:
    print("VOICEVOXは起動済み")

for v in ("1.0", "1.3", "1.6"):
    out = os.path.join(ROOT, "tmp", "voice", "sk_int%s.wav" % v.replace(".", ""))
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "odoku_voice.py"),
         "--script-file", SCRIPT, "--out", out,
         "--intonation", v, "--speed", "0.90", "--style", "ツンギレ"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    line = (r.stdout or r.stderr or "").strip().splitlines()
    print("抑揚%s → %s" % (v, line[-1] if line else "(出力なし)"))
