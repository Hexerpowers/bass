import asyncio
import sys

import cv2 as cv
import time

from vidgear.gears.asyncio.helper import reducer

from .MVL import MVL
from .WebcamVideoStream import WebcamVideoStream

from threading import Thread
import os.path


class Detect:
    def __init__(self, config):
        self.thread = Thread(target=self.detect_data, daemon=False, args=())
        self.started = False
        self.enabled = False

        if not os.path.isfile(config["yolo"]["model_src"]):
            print('Model file not found')
            sys.exit(0)
        if not os.path.isfile(config["yolo"]["cfg_src"]):
            print("YOLO's cfg file not found")
            sys.exit(0)
        if not os.path.isfile(config["yolo"]["names_src"]):
            print('Names file not found')
            sys.exit(0)

        with open(config["yolo"]["names_src"], 'rt') as f:
            self.class_names = f.read().rstrip('\n').split('\n')

        if config["bass"]["mode"] == 'image':
            self.test_image = 1
        else:
            self.test_image = 0

        if self.test_image:
            if os.path.isfile(config["bass"]["source"]):
                self.image_path = config["bass"]["source"]
                print('Test image ready;')
            else:
                print('Test image not found')
                sys.exit(0)
        else:
            self.vs = WebcamVideoStream(config["bass"]["source"]).start()
            if not self.vs.grabbed:
                print('Video file not found or busy')
                sys.exit(0)
            frame = self.vs.read()

        self.net = cv.dnn_DetectionModel(config["yolo"]["cfg_src"], config["yolo"]["model_src"])
        self.net.setInputSize(int(config["yolo"]["size"]), int(config["yolo"]["size"]))
        self.net.setInputScale(1.0 / int(config["yolo"]["scale"]))
        self.net.setInputSwapRB(True)
        print('DNN ready;')

        if bool(int(config["bass"]["use_mavlink"])):
            self.network = MVL(config).start()
            self.use_network = True
            print('Network ready;')
        else:
            self.use_network = False

        self.use_timecodes = bool(int(config["bass"]["use_timecodes"]))
        self.use_display = bool(int(config["bass"]["use_display"]))
        self.config = config

    async def detect_data(self):
        while self.started:
            while self.enabled:
                while True:
                    if self.use_timecodes:
                        start_time = time.time()
                    if self.test_image:
                        frame = cv.imread(self.image_path)
                    else:
                        if not self.vs.grabbed:
                            print('Video file has ended;')
                            sys.exit(0)
                        frame = self.vs.read()
                    classes, confidences, boxes = self.net.detect(frame, confThreshold=0.4, nmsThreshold=0.4)

                    if len(boxes) > 0:
                        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                            # TODO: перенести определение расстояния и угла из теста
                            if self.use_network:
                                self.network.send_mvl(10, 10)
                            label = '%.2f' % confidence
                            label = '%s: %s' % (self.class_names[classId], label)
                            label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                            left, top, width, height = box
                            top = max(top, label_size[1])

                            cv.rectangle(frame, box, color=(0, 255, 0), thickness=3)
                            cv.rectangle(frame, (left, top - label_size[1]),
                                         (left + label_size[0], top + base_line),
                                         (255, 255, 255),
                                         cv.FILLED)
                            cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                    frame = cv.resize(frame, (1200, 700))
                    frame = await reducer(frame, percentage=30)
                    encoded_image = cv.imencode(".jpg", frame)[1].tobytes()
                    yield b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encoded_image + b"\r\n"
                    if self.use_display:
                        cv.imshow('Detect', frame)

                    if self.use_timecodes:
                        print("--- %s seconds ---" % (time.time() - start_time))

                    if self.use_display:
                        if cv.waitKey(27) == 27:
                            cv.destroyAllWindows()
                            self.enabled = False
                            sys.exit(0)

    def start(self):
        if self.started:
            print("There is an instance of Detect running already")
            return None
        self.started = True
        self.thread.start()
        return self

    def stop(self):
        self.started = False
        self.thread.join()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
