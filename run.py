import time
import configparser as cfp
from modules.Detect import Detect

import uvicorn
from vidgear.gears.asyncio import WebGear

start_time = time.time()

options = {
    "frame_size_reduction": 40,
    "frame_jpeg_quality": 80,
    "frame_jpeg_optimize": True,
    "frame_jpeg_progressive": False,
}

web = WebGear(logging=False, **options)

config = cfp.ConfigParser()
config.read("config/bass.cfg")
detect = Detect(config).start()

print('Init finished')

if bool(int(config["bass"]["use_timecodes"])):
    print("--- took %s seconds ---" % (time.time() - start_time))
    print()
detect.enable()
web.config["generator"] = detect.detect_data
uvicorn.run(web(), host="localhost", port=8000)
