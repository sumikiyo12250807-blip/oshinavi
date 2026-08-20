import json, re

raw = open('index.html', encoding='utf-8', newline='').read()
arr = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', raw, re.S).group(1))
byid = {e['id']: e for e in arr}

NL = '\r\n'
def tk_block_with_start(typ, startd, date):
    return (f'      {{{NL}'
            f'        "type": "{typ}",{NL}'
            f'        "startDate": "{startd}",{NL}'
            f'        "date": "{date}"{NL}'
            f'      }}')
def tk_block_no_start(typ, date, sus=False):
    if sus:
        return (f'      {{{NL}'
                f'        "type": "{typ}",{NL}'
                f'        "saleUntilSoldOut": true,{NL}'
                f'        "date": "{date}"{NL}'
                f'      }}')
    return (f'      {{{NL}'
            f'        "type": "{typ}",{NL}'
            f'        "date": "{date}"{NL}'
            f'      }}')

def get_type(eid, idx=0):
    return byid[eid]['tickets'][idx]['type']

reps = []  # (old, new, label)

# ---- B: 本日発売 -> 販売中 (drop startDate, new end date) ----
B = {
    859: ('〜7/1 23:59', '2026-07-01'),
    860: ('〜7/9 23:59', '2026-07-09'),
    865: ('〜9/4 23:59', '2026-09-04'),
    904: ('〜8/14 23:59', '2026-08-14'),
    909: ('〜11/18 23:59', '2026-11-18'),
    918: ('〜6/28 23:59', '2026-06-28'),
    919: ('〜6/25 23:59', '2026-06-25'),
    920: ('〜6/23 23:59', '2026-06-23'),
}
for eid, (suffix, newdate) in B.items():
    old_type = get_type(eid)
    # new type: replace trailing "M/D HH:MM発売" with suffix
    new_type = re.sub(r'）.*$', '）' + suffix, old_type)
    assert new_type != old_type and new_type.endswith(suffix), (eid, old_type, new_type)
    old = tk_block_with_start(old_type, '2026-06-17', '2026-06-17')
    new = tk_block_no_start(new_type, newdate)
    reps.append((old, new, f'B-id{eid}'))

# ---- id856 Arche: 2 tickets -> saleUntilSoldOut, date = show date ----
a856 = byid[856]['tickets']
show856 = ['2026-08-01', '2026-08-14']
for idx, sd in enumerate(show856):
    old_type = a856[idx]['type']
    new_type = re.sub(r'）.*$', '）', old_type)  # strip sale-date suffix
    old = tk_block_with_start(old_type, '2026-06-17', '2026-06-17')
    new = tk_block_no_start(new_type, sd, sus=True)
    reps.append((old, new, f'C-id856[{idx}]'))

# ---- A2: id882 THEカルテット sale end 8/26 -> 8/25 23:59 ----
t882 = get_type(882)  # "...〜8/26"
new882 = re.sub(r'〜8/26$', '〜8/25 23:59', t882)
assert new882 != t882, (t882,)
old = (f'      {{{NL}'
       f'        "type": "{t882}",{NL}'
       f'        "date": "2026-08-26"{NL}'
       f'      }}')
new = (f'      {{{NL}'
       f'        "type": "{new882}",{NL}'
       f'        "date": "2026-08-25"{NL}'
       f'      }}')
reps.append((old, new, 'A2-id882'))

# ---- A1: id887 entry-level date 6/17 -> 7/9 (anchor via dateLabel) ----
dl887 = byid[887]['dateLabel']
old = f'"date": "2026-06-17",{NL}    "dateLabel": "{dl887}"'
new = f'"date": "2026-07-09",{NL}    "dateLabel": "{dl887}"'
reps.append((old, new, 'A1-id887'))

# ---- apply ----
for old, new, label in reps:
    c = raw.count(old)
    if c != 1:
        raise SystemExit(f'[FAIL] {label}: found {c} matches (expected 1)\n--- OLD ---\n{old}')
    raw = raw.replace(old, new, 1)
    print(f'[ok] {label}')

# lone-LF guard
assert len(re.findall(r'(?<!\r)\n', raw)) == 0, 'lone LF introduced!'
open('index.html', 'w', encoding='utf-8', newline='').write(raw)
print('WROTE index.html')
