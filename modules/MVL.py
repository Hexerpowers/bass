from threading import Thread
import time


class MVL:
    def __init__(self, mavlink_ip='', mavlink_port=''):
        self.thread = Thread(target=self.listen_mvl, daemon=True, args=())
        self.started = False

    @staticmethod
    def send_mvl(evt=''):
        print('Event: ' + evt)

    def listen_mvl(self):
        while self.started:
            time.sleep(1)
            # do some listening stuff

    def start(self):
        if self.started:
            print("There is an instance of Network running already")
            return None
        self.started = True
        self.thread.start()
        return self
