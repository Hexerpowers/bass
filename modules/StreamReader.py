from threading import Thread, Lock
import cv2


class StreamReader:
    def __init__(self, config):
        self.thread = Thread(target=self.update, daemon=True, args=())
        self.stream = cv2.VideoCapture(config["bass"]["source"])
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.mode = config["bass"]["mode"]
        self.read_lock = Lock()

    def start(self):
        if self.started:
            print("There is an instance of WebcamVideoStream running already")
            return None
        self.started = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            if grabbed:
                self.grabbed, self.frame = grabbed, frame
            if not grabbed and self.mode == 'video':
                self.stream.set(1, 0)
                if grabbed:
                    self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

    def read(self):
        self.read_lock.acquire()
        frame = self.frame.copy()
        self.read_lock.release()
        return frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self):
        self.stream.release()
