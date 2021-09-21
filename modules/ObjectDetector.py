# coding: utf-8
import math
import time
from datetime import datetime

import cv2 as cv
from aiortc import VideoStreamTrack
from aiortc.mediastreams import MediaStreamError
from av import VideoFrame

from .CourseHandler import CourseHandler
from .Mavlink20 import Mavlink20
from .MetaTransfer import MetaTransfer
from .StreamReader import StreamReader


class ObjectDetector(VideoStreamTrack):
    def __init__(self, config, service):
        super().__init__()
        self.started = False
        self.enabled = False

        self.net = cv.dnn_DetectionModel(config["yolo"]["cfg_src"], config["yolo"]["model_src"])
        self.net.setInputSize(int(config["yolo"]["size"]), int(config["yolo"]["size"]))
        self.net.setInputScale(1.0 / int(config["yolo"]["scale"]))
        self.net.setInputSwapRB(True)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        service.print_log("Bass", 0, "DNN(CUDA mode) ready")

        self.use_timecodes = bool(int(config["bass"]["use_timecodes"]))
        self.use_display = bool(int(config["bass"]["use_display"]))
        self.use_mavlink = bool(int(config["bass"]["use_mavlink"]))
        self.use_meta = bool(int(config["bass"]["use_meta_transfer"]))
        self.use_course = bool(int(config["bass"]["use_course_handler"]))

        self.vs = StreamReader(config).start()
        self.mt = self.use_meta and MetaTransfer(config).start() or None
        self.mav = self.use_mavlink and Mavlink20(config).start() or None
        self.course = self.use_course and CourseHandler(config).start() or None

        self.config = config
        self.service = service
        self.web = None
        self.class_names = service.class_names
        self.test_image = service.test_image
        self.image_path = service.image_path

    async def recv(self):
        if self.use_timecodes:
            start_time = time.time()
        if self.test_image:
            frame = cv.imread(self.image_path)
        else:
            if self.vs is None:
                return MediaStreamError
            while not self.vs.grabbed:
                self.service.print_log("Bass", 1, "No frame available")
            frame = self.vs.read()

        classes, confidences, boxes = self.net.detect(frame, confThreshold=0.2, nmsThreshold=0.2)  # 0.4 0.4
        if len(boxes) > 0:
            if self.use_meta:
                self.mt.send('{class:"jacket", time:"' + str(datetime.now().time()) + '"}')
            mx_conf = max(confidences)
            for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
                if confidence != mx_conf:
                    continue
                label = '%.2f' % confidence
                label = '%s: %s' % (self.class_names[classId], label)
                label_size, base_line = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                left, top, width, height = box
                if self.use_course:
                    (dist, ang) = self.course.calc(box)
                    if dist == 0:
                        dist = "unknown"
                    else:
                        ang = str(math.ceil(ang))
                    if ang == 0:
                        ang = "unknown"
                    else:
                        dist = str(math.ceil(dist))
                else:
                    dist = "unknown"
                    ang = "unknown"
                top = max(top, label_size[1])

                cv.rectangle(frame,
                             (width + 10 + left, height + 10 + top), (left - 10, top - 10),
                             color=(0, 0, 255),
                             thickness=6)
                cv.rectangle(frame, (left - 50, top - label_size[1] - 60),
                             (left + label_size[0] + 150, top + base_line - 20),
                             (255, 255, 255),
                             cv.FILLED)
                cv.putText(frame, label, (left - 50, top - 29), cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0),
                           2)
                # vertical
                cv.line(frame, (960, int(top + height / 2)), (960, 1080), (255, 0, 0), thickness=3)
                # hypot
                cv.line(frame, (960, 1080), (int(left + width / 2), int(top + height / 2)), (0, 255, 0), thickness=3)
                # horizontal
                cv.line(frame, (960, int(top + height / 2)), (int(left + width / 2), int(top + height / 2)),
                        (0, 255, 0), thickness=3)
                cv.circle(frame, (960, 1080),
                          int(math.sqrt(
                              pow((960 - int(left + width / 2)), 2) + pow((1080 - int(top + height / 2)), 2))),
                          (0, 255, 0),
                          thickness=3)
                cv.putText(frame, "Angle: " + ang, (40, 800), cv.FONT_HERSHEY_SIMPLEX, 2.5, (255, 0, 0),
                           4)
                cv.putText(frame, "Distance: " + dist, (40, 880), cv.FONT_HERSHEY_SIMPLEX, 2.5, (255, 0, 0),
                           4)
                frame = cv.resize(frame, (1280, 720))
                # сократить катеты на высоту
            else:
                frame = cv.resize(frame, (1280, 720))

        if self.use_display:
            cv.imshow('Detect', frame)

        if self.use_timecodes:
            self.service.print_log("Bass", 2, "--- took %s seconds ---" % (time.time() - start_time))
        pts, time_base = await self.next_timestamp()
        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base

        return av_frame

    def terminate(self):
        if not (self.vs is None):
            self.vs.__exit__()
            self.vs = None
