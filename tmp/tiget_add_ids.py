# TIGETのイベント番号を指定して組み立てる（番人と同じ関数）→ tmp/built_tiget_ids.json（inject_tiget.py に渡せる形）
#   python tmp/tiget_add_ids.py 520477 523784 522174 523992 --extra tiktoker
import datetime, importlib.util, io, json, sys, time
_KEEP = []


def _load(path, name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


TH = _load('tools/tiget_harvest.py', 'th')
BT = _load('tools/build_tiget_entries.py', 'bt')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
args = sys.argv[1:]
extra = None
if '--extra' in args:
    i = args.index('--extra')
    extra = args[i + 1]
    args = args[:i] + args[i + 2:]
today = datetime.date.today().isoformat()
out, skipped = [], []
for eid in args:
    d = TH.parse_event(TH.fetch('https://tiget.net/events/%s' % eid), eid)
    d['list'] = d.get('list') or {}
    built, why = BT.build(d, today)
    if built:
        if extra:
            built['_extraGenres'] = list(dict.fromkeys((built.get('_extraGenres') or []) + [extra]))
            built['extraGenres'] = [extra]
        out.append(built)
        print('OK  ', eid, built['name'][:50], '| 枠', len(built['tickets']), '| genre', built.get('_genre'))
    else:
        skipped.append((eid, why))
        print('skip', eid, why)
    time.sleep(0.8)
json.dump({'entries': out, 'skipped': skipped}, io.open('tmp/built_tiget_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
