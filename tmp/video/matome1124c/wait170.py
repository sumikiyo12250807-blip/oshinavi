import time, os, datetime
for i in range(34):
    if os.path.exists('C:/Users/user/oshinavi/tmp/video/matome1124c/full1107.done'):
        print('done'); break
    time.sleep(5)
print(datetime.datetime.now().strftime('%H:%M:%S'))
