import time, os, sys
f = 'C:/Users/user/oshinavi/tmp/video/matome1124c/' + sys.argv[1]
for i in range(34):
    if os.path.exists(f):
        print('done'); break
    time.sleep(5)
