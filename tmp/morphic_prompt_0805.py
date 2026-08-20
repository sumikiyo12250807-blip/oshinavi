# -*- coding: utf-8 -*-
"""Morphicのキャンバスに貼るプロンプトを、x_video.py と同じ組み立てで書き出す。
（手打ちで作らない＝ツールと文言がズレると声の対策が効かなくなる）"""
import importlib.util
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('xv', os.path.join(ROOT, 'tools', 'x_video.py'))
xv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xv)

script = io.open(os.path.join(ROOT, 'tmp', 'x_video_script_0805.txt'), encoding='utf-8').read().strip()
prompt = xv.build_prompt(script)
p = os.path.join(ROOT, 'tmp', 'morphic_prompt_0805.txt')
io.open(p, 'w', encoding='utf-8').write(prompt + '\n')
print('セリフ %d字 / プロンプト %d字 -> tmp/morphic_prompt_0805.txt' % (len(script), len(prompt)))
