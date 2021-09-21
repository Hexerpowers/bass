import math
import time
from threading import Thread, Lock

IM_CENTER_X = 960
IM_CENTER_Y = 540
HEIGHT_OFFSET = 1.1


class CourseHandler:
    def __init__(self, config):
        self.confidence = 0

        self.thread = Thread(target=self.reconf, daemon=True, args=())
        self.started = False
        self.read_lock = Lock()

    def start(self):
        if self.started:
            print("There is an instance of CourseHandler running already")
            return None
        self.started = True
        self.thread.start()
        return self

    def stop(self):
        self.started = False
        self.thread.join()

    def calc(self, box):
        self.read_lock.acquire()
        conf = self.confidence
        self.read_lock.release()
        if conf > 20:
            left, top, width, height = box
            dist = (6 * 500 * 1920) / (width * 2.3)
            m_height = int(top + height / 2)
            m_line = IM_CENTER_X - int(left - width / 2)
            m_tg = m_line / m_height
            m_atg = math.atan(m_tg)
            m_angle = math.degrees(m_atg)
        self.read_lock.acquire()
        self.confidence += 1
        self.read_lock.release()
        if conf > 20:
            return (dist, m_angle)
        else:
            return (0, 0)

    def reconf(self):
        while self.started:
            self.read_lock.acquire()
            if self.confidence > 0:
                self.confidence -= 1
            self.read_lock.release()
            time.sleep(0.1)
