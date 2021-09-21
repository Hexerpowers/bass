import os
import sys

from modules.StreamReader import StreamReader


class Service:
    def __init__(self, config):
        self.config = config
        self.class_names = ['object', 'object']
        self.test_image = (config["bass"]["mode"] == 'image') and 1 or 0
        self.image_path = None
        self.vs = None

    def check_config(self):
        if not os.path.isfile(self.config["yolo"]["model_src"]):
            self.print_log("Bass", 1, "Model file not found")
            sys.exit(0)
        if not os.path.isfile(self.config["yolo"]["cfg_src"]):
            self.print_log("Bass", 1, "YOLO's cfg file not found")
            sys.exit(0)
        if self.test_image:
            if os.path.isfile(self.config["bass"]["source"]):
                self.image_path = self.config["bass"]["source"]
                self.print_log("Bass", 0, "Test image ready")
            else:
                self.print_log("Bass", 1, "Test image not found")
                sys.exit(0)
        else:
            self.vs = StreamReader(self.config).start()
            if not self.vs.grabbed:
                print('[error] Video file not found or busy')
                self.vs.stop()
                sys.exit(0)
        self.print_log("Bass", 0, "Config seems to be OK")
        return self

    def print_log(self, src, ltype, message):
        if ltype == 0:
            print("\033[1m\033[34m{}".format(src) + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[33m {}".format("DEBUG") + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[37m {}".format(message))
        elif ltype == 1:
            print("\033[1m\033[34m{}".format(src) + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[35m {}".format("CRITICAL") + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[37m {}".format(message))
        else:
            print("\033[1m\033[34m{}".format(src) + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[37m {}".format("INFO") + "\033[1m\033[31m {}".format("::") +
                  "\033[1m\033[37m {}".format(message))
