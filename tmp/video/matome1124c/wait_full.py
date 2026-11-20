import time, os
for i in range(118):
    if os.path.exists('C:/Users/user/oshinavi/tmp/video/matome1124c/full1107.done'):
        print('done', i * 5); break
    time.sleep(5)
