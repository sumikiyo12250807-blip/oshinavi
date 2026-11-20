import json, io
j = json.load(io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/tempo_check.json'))
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/tempo_top.txt', 'w').write('\n'.join('%s %s' % (k, j[k]) for k in ('kick', 'snare', 'all')) + '\n')
