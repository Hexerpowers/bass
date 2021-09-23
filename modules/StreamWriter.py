import uvicorn
from vidgear.gears.asyncio import WebGear_RTC

from modules.ObjectDetector import ObjectDetector


class StreamWriter:
    def __init__(self, service):
        self.config = service.config
        options = {
            "frame_size_reduction": 20,
            #"enable_live_broadcast": True
        }
        self.vid_host = self.config["vidgear"]["host"]
        self.vid_port = int(self.config["vidgear"]["port"])
        self.web = WebGear_RTC(logging=False, **options)
        self.web.config["server"] = ObjectDetector(self.config, service)

    def start(self):
        uvicorn.run(self.web(), host=self.vid_host, port=self.vid_port, log_level="warning")
        self.web.shutdown()
