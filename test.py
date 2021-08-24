import time

import cv2

from modules.WebcamVideoStream import WebcamVideoStream

vs = WebcamVideoStream('../test/01.mp4').start()
print(vs.grabbed)
while True:
    print(vs.grabbed)
    frame = vs.read()
    cv2.imshow('webcam', frame)
    time.sleep(1)
    if cv2.waitKey(1) == 27:
        break

vs.stop()
cv2.destroyAllWindows()
