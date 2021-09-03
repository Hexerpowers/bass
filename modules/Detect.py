# coding: utf-8
import asyncio
import sys
import codecs

import cv2 as cv
import time

from vidgear.gears.asyncio.helper import reducer
import uvicorn
from vidgear.gears.asyncio import WebGear

from .MVL import MVL
from .WebcamVideoStream import WebcamVideoStream

from threading import Thread
import os.path


class Detect:
    def __init__(self, config):
        self.started = False
        self.enabled = False

        if not os.path.isfile(config["yolo"]["model_src"]):
            print('[error] Model file not found')
            sys.exit(0)
        if not os.path.isfile(config["yolo"]["cfg_src"]):
            print("[error] YOLO's cfg file not found")
            sys.exit(0)
        if not os.path.isfile(config["yolo"]["names_src"]):
            print('[error] Names file not found')
            sys.exit(0)

        with codecs.open(config["yolo"]["names_src"], 'r', encoding='utf-8') as f:
            self.class_names = f.read().rstrip('\n').split('\n')

        if config["bass"]["mode"] == 'image':
            self.test_image = 1
        else:
            self.test_image = 0

        if self.test_image:
            if os.path.isfile(config["bass"]["source"]):
                self.image_path = config["bass"]["source"]
                print('[bass] Test image ready;')
            else:
                print('[error] Test image not found')
                sys.exit(0)
        else:
            self.vs = WebcamVideoStream(config["bass"]["source"]).start()
            if not self.vs.grabbed:
                print('[error] Video file not found or busy')
                sys.exit(0)
            self.vs.read()
        print('[bass] Config seems to be OK;')
        self.net = cv.dnn_DetectionModel(config["yolo"]["cfg_src"], config["yolo"]["model_src"])
        self.net.setInputSize(int(config["yolo"]["size"]), int(config["yolo"]["size"]))
        self.net.setInputScale(1.0 / int(config["yolo"]["scale"]))
        self.net.setInputSwapRB(True)
        print('[bass] DNN ready;')

        if bool(int(config["bass"]["use_mavlink"])):
            self.network = MVL(config).start()
            self.use_network = True
            print('[bass] Network ready;')
        else:
            self.use_network = False

        self.use_timecodes = bool(int(config["bass"]["use_timecodes"]))
        self.use_display = bool(int(config["bass"]["use_display"]))
        self.vid_host = config["vidgear"]["host"]
        self.vid_port = int(config["vidgear"]["port"])
        self.config = config
        self.web = None

    async def detect_data(self):
        while self.started:
            while self.enabled:
                print('[bass] Streaming...')
                while True:
                    if self.use_timecodes:
                        start_time = time.time()
                    if self.test_image:
                        frame = cv.imread(self.image_path)
                    else:
                        if not self.vs.grabbed:
                            print('[bass] Video file has ended;')
                            self.web.shutdown()
                            self.enabled = False
                            break
                        frame = self.vs.read()
                    classes, confidences, boxes = self.net.detect(frame, confThreshold=0.2, nmsThreshold=0.2)  # 0.4 0.4

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
                    encoded_image = cv.imencode(".jpg", frame)[1].tobytes()
                    yield b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encoded_image + b"\r\n"
                    if self.use_display:
                        cv.imshow('Detect', frame)

                    if self.use_timecodes:
                        print("--- %s seconds ---" % (time.time() - start_time))

    def start(self):
        if self.started:
            print("There is an instance of Detect running already")
            return None
        self.started = True
        return self

    def enable(self):
        self.enabled = True
        options = {
            "frame_size_reduction": 0,
            "jpeg_compression_quality": 80,
            "jpeg_compression_fastupsample": True,
            "enable_infinite_frames": True
        }
        self.web = WebGear(logging=False, **options)
        self.web.config["generator"] = self.detect_data
        uvicorn.run(self.web(), host=self.vid_host, port=self.vid_port, log_level="warning")

    def disable(self):
        self.enabled = False
