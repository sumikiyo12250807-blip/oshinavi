# -*- coding: utf-8 -*-
"""ユーザー提示のぴあURLを機械パースして中身を出す（登録判断の材料）。"""
import os, sys, json, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_OUT = sys.__stdout__

s = importlib.util.spec_from_file_location('bpe', os.path.join(TOOLS, 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(s); s.loader.exec_module(bpe)

URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2451557'
try:
    ne = bpe.build({'newid': 999999, 'artist': '', 'urls': [URL]})
except Exception as ex:
    ne = None
    _OUT.write('EXC %s %s\n' % (type(ex).__name__, str(ex)[:200]))

open('tmp/peek_b2451557.json', 'w', encoding='utf-8').write(
    json.dumps(ne, ensure_ascii=False, indent=1) if ne else 'null（買える枠ゼロ）')
_OUT.write('wrote tmp/peek_b2451557.json  tickets=%s\n' % (len(ne['tickets']) if ne else 0))
