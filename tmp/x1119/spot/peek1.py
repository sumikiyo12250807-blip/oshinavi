import sys, os
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\user\AppData\Local\Temp\claude\ac08c5b2b244d5f8\6d0ac969-eb80-4bf7-86e5-551288d024a5\scratchpad\spot1'
start = int(sys.argv[1]); end = int(sys.argv[2])
for f in sys.argv[3:]:
    print('=====', f)
    lines = open(os.path.join(D, f + '.txt'), encoding='utf-8').read().splitlines()
    out = [l for l in lines[start:end] if l not in ('(', ')')]
    print('\n'.join(out))
