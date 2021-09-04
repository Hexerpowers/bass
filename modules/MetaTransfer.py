import socket
import time
from threading import Thread


class MetaTransfer:
    def __init__(self, config):
        self.thread = Thread(target=self.update, daemon=True, args=())
        self.started = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((config["bass"]["tcp_host"], int(config["bass"]["tcp_port"])))
        self.sock.listen(1)
        self.conn = None
        self.addr = None
        self.data = "{}"

    def start(self):
        if self.started:
            print("There is an instance of MetaTransfer running already")
            return None
        self.started = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            self.conn, self.addr = self.sock.accept()
            while True:
                time.sleep(1)
                try:
                    self.conn.send(str.encode(self.data))
                    self.data = "{}"
                except:
                    break

    def send(self, data="{}"):
        self.data = data

    def stop(self):
        self.started = False
        self.thread.join()
