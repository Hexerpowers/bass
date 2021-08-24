from threading import Thread
import time

from pymavlink import mavutil

# TODO: добавить обработку отключения со стороны хоста


class MVL:
    def __init__(self, config):
        self.thread = Thread(target=self.listen_mvl, daemon=True, args=())
        the_connection = mavutil.mavlink_connection(config["mavlink"]["protocol"] + ":" +
                                                    config["mavlink"]["address"] + ":" +
                                                    config["mavlink"]["port"], dialect='common')
        self.connection = the_connection
        self.started = False

    def send_mvl(self, distance=0, angle=0):
        self.connection.mav.param_value_send(b'PERSONDETECTED_D', distance, 9, 2, 0)
        self.connection.mav.param_value_send(b'PERSONDETECTED_A', angle, 9, 2, 1)

    def listen_mvl(self):
        while self.started:
            time.sleep(1)
            msg = self.connection.recv_match(blocking=True)
            print(msg)

    def start(self):
        if self.started:
            print("There is an instance of Network running already")
            return None
        self.started = True
        self.thread.start()
        return self
