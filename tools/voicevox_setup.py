# -*- coding: utf-8 -*-
"""VOICEVOX ENGINE（分割7z）を解凍して置き場所を作る。

GUI版ではなく ENGINE 版を使う理由＝インストーラ不要で、run.exe を起動すれば
localhost:50021 にAPIが立つ＝あたし(Claude)がコマンドから全部叩けるから。
"""
import os
import sys

import multivolumefile
import py7zr

SRC = r"C:\Users\user\Downloads\voicevox_engine.7z"  # 実体は .7z.001
DST = r"C:\Users\user\voicevox_engine"


def main():
    if not os.path.exists(SRC + ".001"):
        print("見つからないわ:", SRC + ".001")
        sys.exit(1)
    os.makedirs(DST, exist_ok=True)
    print("解凍中… %s → %s" % (SRC + ".001", DST))
    with multivolumefile.open(SRC, mode="rb") as vol:
        with py7zr.SevenZipFile(vol) as z:
            z.extractall(path=DST)
    # run.exe を探す（配置はバージョンで変わるので決め打ちしない）
    for root, _dirs, files in os.walk(DST):
        for f in files:
            if f.lower() == "run.exe":
                print("RUN_EXE", os.path.join(root, f))
    print("完了")


main()
